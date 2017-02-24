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
    FlavourInstModel, PortInstModel, SubNetworkInstModel, NfvoRegInfoModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.msapi.nfvolcm import apply_grant_to_nfvo
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class TermVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(TermVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.terminationType = ignore_case_get(self.data, "terminationType")
        self.gracefulTerminationTimeout = ignore_case_get(self.data, "gracefulTerminationTimeout")
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
            # self.query_inst_resource(self.nf_inst_id)
            # self.grant_resource()
            JobUtil.add_job_status(self.job_id, 100, "Terminate Vnf success.")
            is_exist = JobStatusModel.objects.filter(jobid=self.job_id).exists()
            logger.debug("check_ns_inst_name_exist::is_exist=%s" % is_exist)
        except NFLCMException as e:
            logger.error('VNF instantiation failed, detail message: %s' % e.message)
            # NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='failed', lastuptime=now_time())
            JobUtil.add_job_status(self.job_id, 255, e.message)
            # self.vnf_term_failed_handle(e.message)
        except:
            # self.vnf_term_failed_handle('unexpected exception')
            logger.error(traceback.format_exc())

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

    def query_inst_resource(self, inst_id):
        logger.info('[query_resource begin]:inst_id=%s' % inst_id)
        # query_volumn_resource
        vol_list = StorageInstModel.objects.filter(instid=inst_id,
                                                   is_predefined=1)
        for vol in vol_list:
            vol_info = {}
            if not vol.resouceid:
                continue
            vol_info["res_id"] = vol.resouceid
            vol_info["vim_id"] = vol.vimid
            self.inst_resource['volumn'].append(vol_info)
        logger.info('[query_volumn_resource]:ret_volumns=%s' % self.inst_resource['volumn'])

        # query_network_resource
        network_list = NetworkInstModel.objects.filter(instid=inst_id,
                                                       is_predefined=1)
        for network in network_list:
            network_info = {}
            if not network.resouceid:
                continue
            network_info["res_id"] = network.resouceid
            network_info["vim_id"] = network.vimid
            self.inst_resource['network'].append(network_info)
        logger.info('[query_network_resource]:ret_networks=%s' % self.inst_resource['network'])

        # query_subnetwork_resource
        subnetwork_list = SubNetworkInstModel.objects.filter(instid=inst_id,
                                                       is_predefined=1)
        for subnetwork in subnetwork_list:
            subnetwork_info = {}
            if not subnetwork.resouceid:
                continue
            subnetwork_info["res_id"] = subnetwork.resouceid
            subnetwork_info["vim_id"] = subnetwork.vimid
            self.inst_resource['subnet'].append(subnetwork_info)
        logger.info('[query_subnetwork_resource]:ret_networks=%s' % self.inst_resource['subnet'])

        # query_port_resource
        port_list = PortInstModel.objects.filter(instid=inst_id,
                                                       is_predefined=1)
        for port in port_list:
            port_info = {}
            if not port.resouceid:
                continue
            port_info["res_id"] = port.resouceid
            port_info["vim_id"] = port.vimid
            self.inst_resource['port'].append(port_info)
        logger.info('[query_port_resource]:ret_networks=%s' % self.inst_resource['port'])

        # query_flavor_resource
        flavor_list = FlavourInstModel.objects.filter(instid=inst_id,
                                                       is_predefined=1)
        for flavor in flavor_list:
            flavor_info = {}
            if not flavor.resouceid:
                continue
            flavor_info["res_id"] = flavor.resouceid
            flavor_info["vim_id"] = flavor.vimid
            self.inst_resource['flavor'].append(flavor_info)
        logger.info('[query_flavor_resource]:ret_networks=%s' % self.inst_resource['flavor'])

        # query_vm_resource
        vm_list = VmInstModel.objects.filter(instid=inst_id,
                                             is_predefined=1)
        for vm in vm_list:
            vm_info = {}
            if not vm.resouceid:
                continue
            vm_info["res_id"] = vm.resouceid
            vm_info["vim_id"] = vm.vimid
            self.inst_resource['vm'].append(vm_info)
        logger.info('[query_vm_resource]:ret_vms=%s' % self.inst_resource['vm'])

    def grant_resource(self):
        logger.info("nf_cancel_task grant_resource begin")
        JobUtil.add_job_status(self.job_id, 30, 'nf_cancel_task grant_resource')
        reg_info = NfvoRegInfoModel.objects.filter(vnfminstid=self.vnfm_inst_id).first()
        nf_info = NfInstModel.objects.filter(nfinstid=self.vnf_inst_id).first()
        content_args = {'nfvoInstanceId': reg_info.nfvoid, 'vnfmInstanceId': self.vnfm_inst_id,
                        'nfInstanceId': self.vnf_inst_id, 'nfDescriptorId': nf_info.vnf_id,
                        'lifecycleOperation': 'Terminal', 'jobId': '', 'addResource': [],
                        'removeResource': [], 'placementConstraint': [], 'exVimIdList': [], 'additionalParam': {}}

        content_args['removeResource'] = self.get_grant_data()

        logger.info('content_args=%s' % content_args)
        rsp = apply_grant_to_nfvo(content_args)
        logger.info("nf_cancel_task grant_resource rsp: %s" % rsp)
        if rsp[0] != 0:
            logger.error("nf_cancel_task grant_resource failed.[%s]" % str(rsp[1]))
        logger.info("nf_cancel_task grant_resource end")

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
