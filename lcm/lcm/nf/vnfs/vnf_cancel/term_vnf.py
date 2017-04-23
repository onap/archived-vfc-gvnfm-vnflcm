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
from threading import Thread

from lcm.nf.vnfs.const import VNF_STATUS
from lcm.pub.database.models import NfInstModel, VmInstModel, NetworkInstModel, StorageInstModel, \
    FlavourInstModel, PortInstModel, SubNetworkInstModel, VNFCInstModel, NfvoRegInfoModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.msapi.gvnfmdriver import apply_grant_to_nfvo, notify_lcm_to_nfvo
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.vimapi import adaptor

logger = logging.getLogger(__name__)


class TermVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(TermVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.terminationType = ignore_case_get(self.data, "terminationType")
        self.gracefulTerminationTimeout = ignore_case_get(self.data, "gracefulTerminationTimeout")
        self.apply_result = None
        self.notify_data = None
        self.inst_resource = {'volumn': [],
                              'network': [],
                              'subnet': [],
                              'port': [],
                              'flavor': [],
                              'vm': [],
                              }

    def run(self):
        try:
            if self.term_pre():
                self.grant_resource()
                self.query_inst_resource()
                self.query_notify_data()
                self.delete_resource()
                self.lcm_notify()
            JobUtil.add_job_status(self.job_id, 100, "Terminate Vnf success.")
        except NFLCMException as e:
            self.vnf_term_failed_handle(e.message)
        except:
            self.vnf_term_failed_handle(traceback.format_exc())

    def term_pre(self):
        vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if not vnf_insts.exists():
            logger.warn('VnfInst(%s) does not exist' % self.nf_inst_id)
            return False
            #raise NFLCMException('VnfInst(%s) does not exist' % self.nf_inst_id)
        sel_vnf = vnf_insts[0]
        #if sel_vnf.status != 'VNF_INSTANTIATED':
        #    raise NFLCMException("Don't allow to terminate vnf(status:[%s])" % sel_vnf.status)
        if self.terminationType == 'GRACEFUL' and not self.gracefulTerminationTimeout:
            logger.warn("Set Graceful default termination timeout = 60")
            self.gracefulTerminationTimeout = 60
            #raise NFLCMException("Graceful termination must set timeout")

        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status=VNF_STATUS.TERMINATING)
        JobUtil.add_job_status(self.job_id, 10, 'Nf terminating pre-check finish')
        logger.info("Nf terminating pre-check finish")
        return True

    def grant_resource(self):
        logger.info("nf_cancel_task grant_resource begin")
        content_args = {'vnfInstanceId': self.nf_inst_id, 'vnfDescriptorId': '',
                        'lifecycleOperation': 'Terminate', 'jobId': self.job_id,
                        'addResource': [], 'removeResource': [],
                        'placementConstraint': [], 'additionalParam': {}}

        vdus = VmInstModel.objects.filter(instid=self.nf_inst_id, is_predefined=1)
        res_index = 1
        for vdu in vdus:
            res_def = {'type': 'VDU',
                       'resDefId': str(res_index),
                       'resDesId': vdu.resouceid}
            content_args['removeResource'].append(res_def)
            res_index += 1

        vnfmInfo = NfvoRegInfoModel.objects.filter(nfvoid=self.nf_inst_id)
        if len(vnfmInfo) == 0:
            raise NFLCMException('nf_inst_id(%s) does not exist in NfvoRegInfoModel' % self.nf_inst_id)
        content_args['additionalParam']['vnfmid'] = vnfmInfo[0].vnfminstid
        content_args['additionalParam']['vimid'] = vnfmInfo[0].apiurl
        logger.info('content_args=%s' % content_args)
        self.apply_result = apply_grant_to_nfvo(json.dumps(content_args))
        logger.info("nf_cancel_task grant_resource end")
        JobUtil.add_job_status(self.job_id, 20, 'Nf terminating grant_resource finish')

    def query_inst_resource(self):
        logger.info('[query_resource begin]:inst_id=%s' % self.nf_inst_id)
        vol_list = StorageInstModel.objects.filter(instid=self.nf_inst_id)
        for vol in vol_list:
            vol_info = {}
            if not vol.resouceid:
                continue
            vol_info["vim_id"] = vol.vimid
            vol_info["tenant_id"] = vol.tenant
            vol_info["res_id"] = vol.resouceid
            vol_info["is_predefined"] = vol.is_predefined
            self.inst_resource['volumn'].append(vol_info)
        logger.info('[query_volumn_resource]:ret_volumns=%s' % self.inst_resource['volumn'])

        network_list = NetworkInstModel.objects.filter(instid=self.nf_inst_id)
        for network in network_list:
            network_info = {}
            if not network.resouceid:
                continue
            network_info["vim_id"] = network.vimid
            network_info["tenant_id"] = network.tenant
            network_info["res_id"] = network.resouceid
            network_info["is_predefined"] = network.is_predefined
            self.inst_resource['network'].append(network_info)
        logger.info('[query_network_resource]:ret_networks=%s' % self.inst_resource['network'])

        subnetwork_list = SubNetworkInstModel.objects.filter(instid=self.nf_inst_id)
        for subnetwork in subnetwork_list:
            subnetwork_info = {}
            if not subnetwork.resouceid:
                continue
            subnetwork_info["vim_id"] = subnetwork.vimid
            subnetwork_info["tenant_id"] = subnetwork.tenant
            subnetwork_info["res_id"] = subnetwork.resouceid
            subnetwork_info["is_predefined"] = subnetwork.is_predefined
            self.inst_resource['subnet'].append(subnetwork_info)
        logger.info('[query_subnetwork_resource]:ret_networks=%s' % self.inst_resource['subnet'])

        port_list = PortInstModel.objects.filter(instid=self.nf_inst_id)
        for port in port_list:
            port_info = {}
            if not port.resouceid:
                continue
            port_info["vim_id"] = port.vimid
            port_info["tenant_id"] = port.tenant
            port_info["res_id"] = port.resouceid
            port_info["is_predefined"] = port.is_predefined
            self.inst_resource['port'].append(port_info)
        logger.info('[query_port_resource]:ret_networks=%s' % self.inst_resource['port'])

        flavor_list = FlavourInstModel.objects.filter(instid=self.nf_inst_id)
        for flavor in flavor_list:
            flavor_info = {}
            if not flavor.resouceid:
                continue
            flavor_info["vim_id"] = flavor.vimid
            flavor_info["tenant_id"] = flavor.tenant
            flavor_info["res_id"] = flavor.resouceid
            flavor_info["is_predefined"] = flavor.is_predefined
            self.inst_resource['flavor'].append(flavor_info)
        logger.info('[query_flavor_resource]:ret_networks=%s' % self.inst_resource['flavor'])

        vm_list = VmInstModel.objects.filter(instid=self.nf_inst_id)
        for vm in vm_list:
            vm_info = {}
            if not vm.resouceid:
                continue
            vm_info["vim_id"] = vm.vimid
            vm_info["tenant_id"] = vm.tenant
            vm_info["res_id"] = vm.resouceid
            vm_info["is_predefined"] = vm.is_predefined
            self.inst_resource['vm'].append(vm_info)
        logger.info('[query_vm_resource]:ret_vms=%s' % self.inst_resource['vm'])

    def query_notify_data(self):
        logger.info('[NF terminate] send notify request to nfvo start')
        affected_vnfc = []
        vnfcs = VNFCInstModel.objects.filter(instid=self.nf_inst_id)
        for vnfc in vnfcs:
            vm_resource = {}
            if vnfc.vmid:
                vm = VmInstModel.objects.filter(vmid=vnfc.vmid)
                if vm:
                    vm_resource = {'vimId': vm[0].vimid, 'resourceId': vm[0].resouceid,
                                   'resourceName': vm[0].vmname, 'resourceType': 'vm'}
            affected_vnfc.append(
                {'vnfcInstanceId': vnfc.vnfcinstanceid,
                 'vduId': vnfc.vduid,
                 'changeType': 'removed',
                 'computeResource': vm_resource})
        affected_vl = []
        networks = NetworkInstModel.objects.filter(instid=self.nf_inst_id)
        for network in networks:
            network_resource = {'vimId': network.vimid, 'resourceId': network.resouceid,
                                'resourceName': network.name, 'resourceType': 'network'}
            affected_vl.append(
                {'vlInstanceId': network.networkid,
                 'vldid': network.nodeId,
                 'changeType': 'removed',
                 'networkResource': network_resource})
        affected_cp = []
        ports = PortInstModel.objects.filter(instid=self.nf_inst_id)
        for port in ports:
            affected_cp.append(
                {'vsInstanceId': port.portid,
                 'cpdid': port.nodeId,
                 'changeType': 'removed',
                 'storageResource': {'vimId': port.vimid, 'resourceId': port.resouceid,
                                     'resourceName': port.name, 'resourceType': 'port'}})
        affected_vs = []
        vss = StorageInstModel.objects.filter(instid=self.nf_inst_id)
        for vs in vss:
            affected_vs.append(
                {'vsInstanceId': vs.storageid,
                 'vsdId': vs.nodeId,
                 'changeType': 'removed',
                 'storageResource': {'vimId': vs.vimid, 'resourceId': vs.resouceid,
                                     'resourceName': vs.name, 'resourceType': 'volume'}})
        self.notify_data = {
            "status": 'result',
            "vnfInstanceId": self.nf_inst_id,
            "operation": 'Terminal',
            "jobId": self.job_id,
            'affectedVnfc': affected_vnfc,
            'affectedVirtualLink': affected_vl,
            'affectedVirtualStorage': affected_vs,
            'affectedCp': affected_cp
            }
        vnfmInfo = NfvoRegInfoModel.objects.filter(nfvoid=self.nf_inst_id)
        if len(vnfmInfo) == 0:
            raise NFLCMException('nf_inst_id(%s) does not exist in NfvoRegInfoModel' % self.nf_inst_id)
        self.notify_data['VNFMID'] = vnfmInfo[0].vnfminstid
        logger.info('content_args=%s' % self.notify_data)

    def delete_resource(self):
        logger.info('rollback resource begin')
        adaptor.delete_vim_res(self.inst_resource, self.do_notify_delete)
        logger.info('rollback resource complete')

    def do_notify_delete(self, res_type, res_id):
        logger.error('Deleting [%s] resource:resourceid [%s]' % (res_type, res_id))
        if res_type == adaptor.RES_VM:
            VmInstModel.objects.filter(instid=self.nf_inst_id, resouceid=res_id).delete()
        elif res_type == adaptor.RES_FLAVOR:
            FlavourInstModel.objects.filter(instid=self.nf_inst_id, resouceid=res_id).delete()
        elif res_type == adaptor.RES_PORT:
            PortInstModel.objects.filter(instid=self.nf_inst_id, resouceid=res_id).delete()
        elif res_type == adaptor.RES_SUBNET:
            SubNetworkInstModel.objects.filter(instid=self.nf_inst_id, resouceid=res_id).delete()
        elif res_type == adaptor.RES_NETWORK:
            NetworkInstModel.objects.filter(instid=self.nf_inst_id, resouceid=res_id).delete()
        elif res_type == adaptor.RES_VOLUME:
            StorageInstModel.objects.filter(instid=self.nf_inst_id, resouceid=res_id).delete()

    def lcm_notify(self):
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='NOT_INSTANTIATED', lastuptime=now_time())
        logger.info('[NF termination] send notify request to nfvo end')
        resp = notify_lcm_to_nfvo(self.notify_data)
        logger.info('[NF termination] get lcm response %s' % resp)
        logger.info('[NF termination] send notify request to nfvo end')

    def vnf_term_failed_handle(self, error_msg):
        logger.error('VNF termination failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='failed', lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, error_msg)
