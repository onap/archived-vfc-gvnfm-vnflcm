# Copyright 2017 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import logging
import traceback
import uuid
from threading import Thread

from lcm.nf.vnfs.const import vnfd_model_dict
from lcm.pub.database.models import NfInstModel, VmInstModel, NetworkInstModel, \
    SubNetworkInstModel, PortInstModel, StorageInstModel, FlavourInstModel, VNFCInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.msapi.catalog import query_rawdata_from_catalog
from lcm.pub.msapi.nfvolcm import apply_grant_to_nfvo, notify_lcm_to_nfvo, get_packageinfo_by_vnfdid
from lcm.pub.utils import toscautil
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get, get_none, get_boolean
from lcm.pub.vimapi import adaptor

logger = logging.getLogger(__name__)


class InstVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(InstVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.nfvo_inst_id = ''
        self.vnfm_inst_id = ''
        self.csar_id = ''
        self.vnfd_info = []
        # self.inst_resource = {'volumn': [],  # [{"vim_id": ignore_case_get(ret, "vim_id")},{}]
        #                       'network': [],
        #                       'subnet': [],
        #                       'port': [],
        #                       'flavor': [],
        #                       'vm': [],
        #                       }

    def run(self):
        try:
            self.inst_pre()
            self.apply_grant()
            self.create_res()
            self.lcm_notify()
            JobUtil.add_job_status(self.job_id, 100, "Instantiate Vnf success.")
        except NFLCMException as e:
            self.vnf_inst_failed_handle(e.message)
        except:
            self.vnf_inst_failed_handle('unexpected exception')

    def inst_pre(self):
        vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if not vnf_insts.exists():
            raise NFLCMException('VNF nf_inst_id is not exist.')

        # self.vnfm_inst_id = vnf_insts[0].vnfm_inst_id
        if vnf_insts[0].status != 'NOT_INSTANTIATED':
            raise NFLCMException('VNF instantiationState is not NOT_INSTANTIATED.')

        JobUtil.add_job_status(self.job_id, 5, 'Get packageinfo by vnfd_id')
        # get csar_id from nslcm by vnfd_id
        self.package_info = get_packageinfo_by_vnfdid(vnf_insts[0].vnfdid)
        self.package_id = ignore_case_get(self.package_info, "package_id")
        self.csar_id = ignore_case_get(self.package_info, "csar_id")

        JobUtil.add_job_status(self.job_id, 10, 'Get rawdata from catalog by csar_id')
        # get rawdata from catalog by csar_id
        input_parameters = []
        for key, val in self.data['additionalParams'].items():
            input_parameters.append({"key": key, "value": val})
        raw_data = query_rawdata_from_catalog(self.csar_id, input_parameters)
        self.vnfd_info = toscautil.convert_vnfd_model(raw_data["rawData"])  # convert to inner json
        self.vnfd_info = json.JSONDecoder().decode(self.vnfd_info)

        self.vnfd_info = vnfd_model_dict  # just for test

        self.checkParameterExist()
        # update NfInstModel
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).\
            update(flavour_id=ignore_case_get(self.data, "flavourId"),
                   input_params=self.data,
                   vnfd_model=self.vnfd_info,
                   localizationLanguage=ignore_case_get(self.data, 'localizationLanguage'),
                   lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 15, 'Nf instancing pre-check finish')
        logger.info("Nf instancing pre-check finish")

    def apply_grant(self):
        logger.info('[NF instantiation] send resource grand request to nfvo start')
        # self.check_vm_capacity()
        content_args = {'vnfInstanceId': self.nf_inst_id, 'vnfDescriptorId': '',
                        'lifecycleOperation': 'Instantiate', 'jobId': self.job_id,
                        'addResource': [], 'removeResource': [],
                        'placementConstraint': [], 'additionalParam': {}}

        vdus = ignore_case_get(self.vnfd_info, "vdus")
        res_index = 1
        for vdu in vdus:
            res_def = {'type': 'VDU',
                       'resDefId': str(res_index),
                       'resDesId': ignore_case_get(vdu, "vdu_id")}
            content_args['addResource'].append(res_def)
            res_index += 1

        logger.info('content_args=%s' % content_args)
        self.apply_result = apply_grant_to_nfvo(content_args)
        vim_info = ignore_case_get(self.apply_result, "vim")

        # update vnfd_info
        for vdu in self.vnfd_info["vdus"]:
            if "location_info" in vdu["properties"]:
                vdu["properties"]["location_info"]["vimid"] = ignore_case_get(vim_info, "vimid")
                vdu["properties"]["location_info"]["tenant"] = ignore_case_get(
                    ignore_case_get(vim_info, "accessinfo"), "tenant")
            else:
                vdu["properties"]["location_info"] = {"vimid":ignore_case_get(vim_info, "vimid"),
                                                      "tenant":ignore_case_get(
                                                          ignore_case_get(vim_info, "accessinfo"), "tenant")}

        # update resources_table
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='INSTANTIATED', lastuptime=now_time())
        JobUtil.add_job_status(self.job_id,20, 'Nf instancing apply grant finish')
        logger.info("Nf instancing apply grant finish")

    def create_res(self):
        logger.info("[NF instantiation] create resource start")
        adaptor.create_vim_res(self.vnfd_info, self.do_notify)

        JobUtil.add_job_status(self.job_id, 70, '[NF instantiation] create resource finish')
        logger.info("[NF instantiation] create resource finish")

    def lcm_notify(self):
        logger.info('[NF instantiation] send notify request to nfvo start')
        affected_vnfc = []
        vnfcs = VNFCInstModel.objects.filter(instid=self.nf_inst_id)
        for vnfc in vnfcs:
            vmResource = {}
            if vnfc.vmid:
                vm = VmInstModel.objects.filter(vmid=vnfc.vmid)
                if vm:
                    vmResource = {'vimId': vm[0].vimid, 'resourceId': vm[0].resouceid,
                                  'resourceName': vm[0].vmname, 'resourceType': 'vm'}
            affected_vnfc.append(
                {'vnfcInstanceId': vnfc.vnfcinstanceid,
                 'vduId': vnfc.vduid,
                 'changeType': 'added',
                 'computeResource': vmResource})
        affected_vl = []
        networks = NetworkInstModel.objects.filter(instid=self.nf_inst_id)
        for network in networks:
            network_resource = {'vimId': network.vimid, 'resourceId': network.resouceid,
                                'resourceName': network.name, 'resourceType': 'network'}
            affected_vl.append(
                {'vlInstanceId': network.networkid,
                 'vldid': network.nodeId,
                 'changeType': 'added',
                 'networkResource': network_resource})
        affected_cp = []
        ports = PortInstModel.objects.filter(instid=self.nf_inst_id)
        for port in ports:
            affected_cp.append(
                {'vsInstanceId': port.portid,
                 'cpdid': port.nodeId,
                 'changeType': 'added',
                 'storageResource': {'vimId': port.vimid, 'resourceId': port.resouceid,
                                     'resourceName': port.name, 'resourceType': 'port'}})
        affected_vs = []
        vss = StorageInstModel.objects.filter(instid=self.nf_inst_id)
        for vs in vss:
            affected_vs.append(
                {'vsInstanceId': vs.storageid,
                 'vsdId': vs.nodeId,
                 'changeType': 'added',
                 'storageResource': {'vimId': vs.vimid, 'resourceId': vs.resouceid,
                                     'resourceName': vs.name, 'resourceType': 'volume'}})
        content_args = {
            "status": 'result',
            "nfInstanceId": self.nf_inst_id,
            "operation": 'instantiate',
            "jobId": self.job_id,
            'affectedVnfc': affected_vnfc,
            'affectedVirtualLink': affected_vl,
            'affectedVirtualStorage': affected_vs,
            # "vnfdmodule": allocate_data,
            # "additionalParam": addition_param,
            # "nfvoInstanceId": self.nfvo_inst_id,
            # "vnfmInstanceId": self.vnfm_inst_id,
            # 'affectedcapacity': affectedcapacity,
            # 'affectedService': [],
            'affectedCp': affected_cp
            }
        logger.info('content_args=%s' % content_args)
        # call rest api
        resp = notify_lcm_to_nfvo(content_args, self.nf_inst_id)
        logger.info('[NF instantiation] get lcm response %s' % resp)
        logger.info('[NF instantiation] send notify request to nfvo end')

    # def load_nfvo_config(self):
    #     logger.info("[NF instantiation]get nfvo connection info start")
    #     reg_info = NfvoRegInfoModel.objects.filter(vnfminstid='vnfm111').first()
    #     if reg_info:
    #         self.vnfm_inst_id = reg_info.vnfminstid
    #         self.nfvo_inst_id = reg_info.nfvoid
    #         logger.info("[NF instantiation] Registered nfvo id is [%s]" % self.nfvo_inst_id)
    #     else:
    #         raise NFLCMException("Nfvo was not registered")
    #     logger.info("[NF instantiation]get nfvo connection info end")

    def vnf_inst_failed_handle(self, error_msg):
        logger.error('VNF instantiation failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='failed', lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, error_msg)

    def do_notify(self, res_type, ret):
        logger.info('creating [%s] resource' % res_type)
        # progress = 20 + int(progress/2)     # 20-70
        if res_type == adaptor.RES_VOLUME:
            logger.info('Create vloumns!')
            # if ret["returnCode"] == adaptor.RES_NEW:  # new create
            #     self.inst_resource['volumn'].append({"vim_id": ignore_case_get(ret, "vim_id"),
            #                                          "res_id": ignore_case_get(ret, "res_id")})
            JobUtil.add_job_status(self.job_id, 25, 'Create vloumns!')
            StorageInstModel.objects.create(
                storageid=str(uuid.uuid4()),
                vimid=ignore_case_get(ret, "vimId"),
                resouceid=ignore_case_get(ret, "id"),
                name=ignore_case_get(ret, "name"),
                tenant=ignore_case_get(ret, "tenantId"),
                create_time=ignore_case_get(ret, "createTime"),
                storagetype=get_none(ignore_case_get(ret, "type")),
                size=ignore_case_get(ret, "size"),
                insttype=0,
                is_predefined=ignore_case_get(ret, "returnCode"),
                nodeId=ignore_case_get(ret, "nodeId"),
                instid=self.nf_inst_id)
        elif res_type == adaptor.RES_NETWORK:
            logger.info('Create networks!')
            # if ret["returnCode"] == adaptor.RES_NEW:
            #     self.inst_resource['network'].append({"vim_id": ignore_case_get(ret, "vim_id"),
            #                                           "res_id": ignore_case_get(ret, "res_id")})
            # self.inst_resource['network'].append({"vim_id": "1"}, {"res_id": "2"})
            JobUtil.add_job_status(self.job_id, 35, 'Create networks!')
            NetworkInstModel.objects.create(
                networkid=str(uuid.uuid4()),
                name=ignore_case_get(ret, "name"),
                vimid=ignore_case_get(ret, "vimId"),
                resouceid=ignore_case_get(ret, "id"),
                tenant=ignore_case_get(ret, "tenantId"),
                segmentid=str(ignore_case_get(ret, "segmentationId")),
                network_type=ignore_case_get(ret, "networkType"),
                physicalNetwork=ignore_case_get(ret, "physicalNetwork"),
                vlantrans=get_boolean(ignore_case_get(ret, "vlanTransparent")),
                is_shared=get_boolean(ignore_case_get(ret, "shared")),
                routerExternal=get_boolean(ignore_case_get(ret, "routerExternal")),
                insttype = 0,
                is_predefined=ignore_case_get(ret, "returnCode"),
                nodeId=ignore_case_get(ret, "nodeId"),
                instid = self.nf_inst_id)
        elif res_type == adaptor.RES_SUBNET:
            logger.info('Create subnets!')
            # if ret["returnCode"] == adaptor.RES_NEW:
            #     self.inst_resource['subnet'].append({"vim_id": ignore_case_get(ret, "vim_id"),
            #                                          "res_id": ignore_case_get(ret, "res_id")})
            # self.inst_resource['subnet'].append({"vim_id": "1"}, {"res_id": "2"})
            JobUtil.add_job_status(self.job_id, 40, 'Create subnets!')
            SubNetworkInstModel.objects.create(
                subnetworkid=str(uuid.uuid4()),
                name=ignore_case_get(ret, "name"),
                vimid=ignore_case_get(ret, "vimId"),
                resouceid=ignore_case_get(ret, "id"),
                tenant=ignore_case_get(ret, "tenantId"),
                networkid=ignore_case_get(ret, "networkId"),
                cidr=ignore_case_get(ret, "cidr"),
                ipversion=ignore_case_get(ret, "ipversion"),
                isdhcpenabled=ignore_case_get(ret, "enableDhcp"),
                gatewayip=ignore_case_get(ret, "gatewayIp"),
                dnsNameservers=ignore_case_get(ret, "dnsNameservers"),
                hostRoutes=ignore_case_get(ret, "hostRoutes"),
                allocationPools=ignore_case_get(ret, "allocationPools"),
                insttype=0,
                is_predefined=ignore_case_get(ret, "returnCode"),
                instid=self.nf_inst_id)
        elif res_type == adaptor.RES_PORT:
            logger.info('Create ports!')
            # if ret["returnCode"] == adaptor.RES_NEW:
            #     self.inst_resource['port'].append({"vim_id": ignore_case_get(ret, "vim_id"),
            #                                        "res_id": ignore_case_get(ret, "res_id")})
            # self.inst_resource['port'].append({"vim_id": "1"}, {"res_id": "2"})
            JobUtil.add_job_status(self.job_id, 50, 'Create ports!')
            PortInstModel.objects.create(
                portid=str(uuid.uuid4()),
                networkid=ignore_case_get(ret, "networkId"),
                subnetworkid=ignore_case_get(ret, "subnetId"),
                name=ignore_case_get(ret, "name"),
                vimid=ignore_case_get(ret, "vimId"),
                resouceid=ignore_case_get(ret, "id"),
                tenant=ignore_case_get(ret, "tenantId"),
                macaddress = ignore_case_get(ret, "macAddress"),
                ipaddress = ignore_case_get(ret, "ip"),
                typevirtualnic=ignore_case_get(ret, "vnicType"),
                securityGroups=ignore_case_get(ret, "securityGroups"),
                insttype=0,
                is_predefined=ignore_case_get(ret, "returnCode"),
                nodeId=ignore_case_get(ret, "nodeId"),
                instid=self.nf_inst_id)
        elif res_type == adaptor.RES_FLAVOR:
            logger.info('Create flavors!')
            # if ret["returnCode"] == adaptor.RES_NEW:
            #     self.inst_resource['flavor'].append({"vim_id": ignore_case_get(ret, "vim_id"),
            #                                          "res_id": ignore_case_get(ret, "res_id")})
            # self.inst_resource['flavor'].append({"vim_id": "1"}, {"res_id": "2"})
            JobUtil.add_job_status(self.job_id, 60, 'Create flavors!')
            FlavourInstModel.objects.create(
                flavourid=str(uuid.uuid4()),
                name=ignore_case_get(ret, "name"),
                vimid=ignore_case_get(ret, "vimId"),
                resouceid=ignore_case_get(ret, "id"),
                tenant=ignore_case_get(ret, "tenantId"),
                vcpu=ignore_case_get(ret, "vcpu"),
                memory=ignore_case_get(ret, "memory"),
                disk=ignore_case_get(ret, "disk"),
                ephemeral=ignore_case_get(ret, "ephemeral"),
                swap=ignore_case_get(ret, "swap"),
                isPublic=get_boolean(ignore_case_get(ret, "isPublic")),
                extraspecs=ignore_case_get(ret, "extraSpecs"),
                is_predefined=ignore_case_get(ret, "returnCode"),
                instid=self.nf_inst_id)
        elif res_type == adaptor.RES_VM:
            logger.info('Create vms!')
            # if ret["returnCode"] == adaptor.RES_NEW:
            #     self.inst_resource['vm'].append({"vim_id": ignore_case_get(ret, "vim_id"),
            #                                      "res_id": ignore_case_get(ret, "res_id")})
            # self.inst_resource['vm'].append({"vim_id": "1"}, {"res_id": "2"})
            JobUtil.add_job_status(self.job_id, 70, 'Create vms!')
            vm_id = str(uuid.uuid4())
            VmInstModel.objects.create(
                vmid=vm_id,
                vmname=ignore_case_get(ret, "name"),
                vimid=ignore_case_get(ret, "vimId"),
                resouceid=ignore_case_get(ret, "id"),
                tenant=ignore_case_get(ret, "tenantId"),
                nic_array=ignore_case_get(ret, "nicArray"),
                metadata=ignore_case_get(ret, "metadata"),
                volume_array=ignore_case_get(ret, "volumeArray"),
                server_group=ignore_case_get(ret, "serverGroup"),
                availability_zone=ignore_case_get(ret, "availabilityZone"),
                flavor_id=ignore_case_get(ret, "flavorId"),
                security_groups=ignore_case_get(ret, "securityGroups"),
                operationalstate=ignore_case_get(ret, "status"),
                insttype=0,
                is_predefined=ignore_case_get(ret, "returnCode"),
                instid=self.nf_inst_id)
            VNFCInstModel.objects.create(
                vnfcinstanceid=str(uuid.uuid4()),
                vduid=ignore_case_get(ret, "id"),
                is_predefined=ignore_case_get(ret, "returnCode"),
                instid=self.nf_inst_id,
                vmid=vm_id)

    # def do_rollback(self, args_=None):
    #     logger.error('error info : %s' % args_)
    #     adaptor.delete_vim_res(self.inst_resource, self.do_notify_delete)
    #     logger.error('rollback resource complete')
    #
    #     StorageInstModel.objects.filter(instid=self.nf_inst_id).delete()
    #     NetworkInstModel.objects.filter(instid=self.nf_inst_id).delete()
    #     SubNetworkInstModel.objects.filter(instid=self.nf_inst_id).delete()
    #     PortInstModel.objects.filter(instid=self.nf_inst_id).delete()
    #     FlavourInstModel.objects.filter(instid=self.nf_inst_id).delete()
    #     VmInstModel.objects.filter(instid=self.nf_inst_id).delete()
    #     logger.error('delete table complete')
    #     raise NFLCMException("Create resource failed")
    #
    # def do_notify_delete(self, ret):
    #     logger.error('Deleting [%s] resource' % ret)

    def checkParameterExist(self):
        # if ignore_case_get(self.data, "flavourId") not in self.vnfd_info:
        #     raise NFLCMException('Input parameter is not defined in vnfd_info.')
        pass
