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
import logging
import traceback
from threading import Thread

from lcm.nf.vnfs.const import VNF_STATUS
from lcm.pub.database.models import JobStatusModel, NfInstModel, VmInstModel, NetworkInstModel, StorageInstModel, \
    FlavourInstModel, PortInstModel, SubNetworkInstModel, VNFCInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.msapi.nfvolcm import apply_grant_to_nfvo, notify_lcm_to_nfvo
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
        self.inst_resource = {'volumn': [],  # [{"vim_id": ignore_case_get(ret, "vim_id")},{}]
                              'network': [],
                              'subnet': [],
                              'port': [],
                              'flavor': [],
                              'vm': [],
                              }

    def run(self):
        try:
            self.term_pre()
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
            raise NFLCMException('VnfInst(%s) does not exist' % self.nf_inst_id)
        sel_vnf = vnf_insts[0]
        if sel_vnf.status != 'VNF_INSTANTIATED':
            raise NFLCMException("Don't allow to delete vnf(status:[%s])" % sel_vnf.status)
        if self.terminationType == 'GRACEFUL' and not self.gracefulTerminationTimeout:
            raise NFLCMException("Graceful termination must set timeout")

        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status=VNF_STATUS.TERMINATING)
        JobUtil.add_job_status(self.job_id, 10, 'Nf terminating pre-check finish')
        logger.info("Nf terminating pre-check finish")

    def grant_resource(self):
        logger.info("nf_cancel_task grant_resource begin")
        content_args = {'vnfInstanceId': self.nf_inst_id, 'vnfDescriptorId': '',
                        'lifecycleOperation': 'Instantiate', 'jobId': self.job_id,
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

        logger.info('content_args=%s' % content_args)
        self.apply_result = apply_grant_to_nfvo(content_args)
        logger.info("nf_cancel_task grant_resource end")
        JobUtil.add_job_status(self.job_id, 20, 'Nf terminating grant_resource finish')

    def query_inst_resource(self):
        logger.info('[query_resource begin]:inst_id=%s' % self.nf_inst_id)
        # query_volumn_resource
        vol_list = StorageInstModel.objects.filter(instid=self.nf_inst_id, is_predefined=1)
        for vol in vol_list:
            vol_info = {}
            if not vol.resouceid:
                continue
            vol_info["vim_id"] = vol.vimid
            vol_info["tenant_id"] = vol.tenant
            vol_info["res_id"] = vol.resouceid
            self.inst_resource['volumn'].append(vol_info)
        logger.info('[query_volumn_resource]:ret_volumns=%s' % self.inst_resource['volumn'])

        # query_network_resource
        network_list = NetworkInstModel.objects.filter(instid=self.nf_inst_id, is_predefined=1)
        for network in network_list:
            network_info = {}
            if not network.resouceid:
                continue
            network_info["vim_id"] = network.vimid
            network_info["tenant_id"] = network.tenant
            network_info["res_id"] = network.resouceid
            self.inst_resource['network'].append(network_info)
        logger.info('[query_network_resource]:ret_networks=%s' % self.inst_resource['network'])

        # query_subnetwork_resource
        subnetwork_list = SubNetworkInstModel.objects.filter(instid=self.nf_inst_id, is_predefined=1)
        for subnetwork in subnetwork_list:
            subnetwork_info = {}
            if not subnetwork.resouceid:
                continue
            subnetwork_info["vim_id"] = subnetwork.vimid
            subnetwork_info["tenant_id"] = subnetwork.tenant
            subnetwork_info["res_id"] = subnetwork.resouceid
            self.inst_resource['subnet'].append(subnetwork_info)
        logger.info('[query_subnetwork_resource]:ret_networks=%s' % self.inst_resource['subnet'])

        # query_port_resource
        port_list = PortInstModel.objects.filter(instid=self.nf_inst_id, is_predefined=1)
        for port in port_list:
            port_info = {}
            if not port.resouceid:
                continue
            port_info["vim_id"] = port.vimid
            port_info["tenant_id"] = port.tenant
            port_info["res_id"] = port.resouceid
            self.inst_resource['port'].append(port_info)
        logger.info('[query_port_resource]:ret_networks=%s' % self.inst_resource['port'])

        # query_flavor_resource
        flavor_list = FlavourInstModel.objects.filter(instid=self.nf_inst_id, is_predefined=1)
        for flavor in flavor_list:
            flavor_info = {}
            if not flavor.resouceid:
                continue
            flavor_info["vim_id"] = flavor.vimid
            flavor_info["tenant_id"] = flavor.tenant
            flavor_info["res_id"] = flavor.resouceid
            self.inst_resource['flavor'].append(flavor_info)
        logger.info('[query_flavor_resource]:ret_networks=%s' % self.inst_resource['flavor'])

        # query_vm_resource
        vm_list = VmInstModel.objects.filter(instid=self.nf_inst_id, is_predefined=1)
        for vm in vm_list:
            vm_info = {}
            if not vm.resouceid:
                continue
            vm_info["vim_id"] = vm.vimid
            vm_info["tenant_id"] = vm.tenant
            vm_info["res_id"] = vm.resouceid
            self.inst_resource['vm'].append(vm_info)
        logger.info('[query_vm_resource]:ret_vms=%s' % self.inst_resource['vm'])

    def query_notify_data(self):
        logger.info('[NF instantiation] send notify request to nfvo start')
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
            "nfInstanceId": self.nf_inst_id,
            "operation": 'Terminal',
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
        logger.info('content_args=%s' % self.notify_data)

    def delete_resource(self):
        logger.error('rollback resource begin')
        adaptor.delete_vim_res(self.inst_resource, self.do_notify_delete)
        logger.error('rollback resource complete')

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
        resp = notify_lcm_to_nfvo(self.notify_data, self.nf_inst_id)
        logger.info('[NF termination] get lcm response %s' % resp)
        logger.info('[NF termination] send notify request to nfvo end')

    def vnf_term_failed_handle(self, error_msg):
        logger.error('VNF termination failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='failed', lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, error_msg)
