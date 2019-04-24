# Copyright 2019 ZTE Corporation.
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

from lcm.nf.biz.common import port_save
from lcm.nf.biz.grant_vnf import grant_resource
from lcm.nf.const import RESOURCE_MAP, GRANT_TYPE, OPERATION_STATE_TYPE
from lcm.nf.const import VNF_STATUS, OPERATION_TASK, OPERATION_TYPE
from lcm.pub.database.models import VmInstModel, NfInstModel, PortInstModel
from lcm.pub.utils.notificationsutil import NotificationsUtil, prepare_notification
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.exceptions import NFLCMException
from lcm.pub.vimapi import adaptor
from .operate_vnf_lcm_op_occ import VnfLcmOpOcc

logger = logging.getLogger(__name__)


class ChangeExtConn(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(ChangeExtConn, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        self.extVirtualLinks = ignore_case_get(self.data, "extVirtualLinks")
        self.vimConnectionInfo = ignore_case_get(self.data, "vimConnectionInfo")
        self.additionalParams = ignore_case_get(self.data, "additionalParams")
        self.lcm_op_occ = VnfLcmOpOcc(
            vnf_inst_id = nf_inst_id,
            lcm_op_id = job_id,
            operation = OPERATION_TYPE.CHANGE_EXT_CONN,
            task = OPERATION_TASK.CHANGE_EXT_CONN
        )

    def run(self):
        try:
            self.lcm_op_occ.notify_lcm(OPERATION_STATE_TYPE.STARTING)
            JobUtil.add_job_status(self.job_id,
                                   10,
                                   "Start to apply grant.")
            self.apply_grant()
            self.lcm_op_occ.notify_lcm(OPERATION_STATE_TYPE.PROCESSING)
            JobUtil.add_job_status(self.job_id,
                                   50,
                                   "Start to change ext conn.")
            self.do_operation()
            self.vnf_insts.update(
                status='INSTANTIATED',
                lastuptime=now_time()
            )
            self.lcm_op_occ.notify_lcm(OPERATION_STATE_TYPE.COMPLETED)
            JobUtil.add_job_status(self.job_id,
                                   100,
                                   "Change ext conn success.")
        except NFLCMException as e:
            logger.error(e.message)
            self.change_ext_conn_failed_handle(e.message)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            self.change_ext_conn_failed_handle(e.message)

    def apply_grant(self):
        vdus = VmInstModel.objects.filter(instid=self.nf_inst_id)
        apply_result = grant_resource(data=self.data,
                                      nf_inst_id=self.nf_inst_id,
                                      job_id=self.job_id,
                                      grant_type=GRANT_TYPE.CHANGE_CONNECTIVITY,
                                      vdus=vdus)
        logger.debug("Grant resource end, response: %s" % apply_result)

    def do_operation(self):
        logger.info('Operation resource begin')
        logger.debug("self.vimConnectionInfo: %s" % self.vimConnectionInfo)
        vnfd_info = json.loads(self.vnf_insts[0].vnfd_model)
        vm_id = ignore_case_get(self.additionalParams, "vmid")
        if not vm_id:
            vms = VmInstModel.objects.filter(instid=self.nf_inst_id)
            vm_id = vms[0].resourceid
        vim_id = ignore_case_get(self.vimConnectionInfo[0], "vimid")
        accessInfo = ignore_case_get(self.vimConnectionInfo[0], "accessInfo")
        tenant = ignore_case_get(accessInfo, "tenant")

        self.vim_cache, self.res_cache = {}, {}
        for extVirtualLink in self.extVirtualLinks:
            network_id = ignore_case_get(extVirtualLink, "resourceId")
            ext_cps = ignore_case_get(extVirtualLink, "extCps")
            for ext_cp in ext_cps:
                cpd_id = ignore_case_get(ext_cp, "cpdId")
                cp_config = ignore_case_get(ext_cp, "cpConfig")
                # cp_instance_id = ignore_case_get(cp_config[0], "cpInstanceId")
                cp_protocol_data = ignore_case_get(cp_config[0], "cpProtocolData")
                # mac_address = ignore_case_get(ignore_case_get(cp_protocol_data[0], "ipOverEthernet"), "macAddress")
                ip_addresses = ignore_case_get(ignore_case_get(cp_protocol_data[0], "ipOverEthernet"), "ipAddresses")
                # fixed_addresse = ignore_case_get(ip_addresses[0], "fixedAddresses")[0]
                # addressRange = ignore_case_get(ip_addresses[0], "addressRange")
                # minAddress = ignore_case_get(addressRange, "minAddress")
                # maxAddress = ignore_case_get(addressRange, "maxAddress")
                subnet_id = ignore_case_get(ip_addresses[0], "subnetId")

                vdu_id = ""
                cps = ignore_case_get(vnfd_info, "cps")
                for cp in cps:
                    cpd_id_in_model = ignore_case_get(cp, "cpd_id")
                    if cpd_id == cpd_id_in_model:
                        vdu_id = ignore_case_get(cp, "vdu_id")
                        break

                port = {
                    "cp_id": cpd_id,
                    "cpd_id": cpd_id,
                    "vm_id": vm_id,
                    "description": "",
                    "properties": {
                        # "name": "",
                        # "mac_address": mac_address,
                        # "ip_address:": fixed_addresse,
                        # "ip_range_start": minAddress,
                        # "ip_range_end": maxAddress,
                        "location_info": {
                            "vimid": vim_id,
                            "tenant": tenant
                        }
                    },
                    "vl_id": network_id,
                    "vdu_id": vdu_id,
                    "networkId": network_id,
                    "subnetId": subnet_id
                }
                for resource_type in ['vdus', 'vls', 'cps', 'volume_storages']:
                    for resource in ignore_case_get(vnfd_info, resource_type):
                        if "location_info" not in resource["properties"]:
                            resource["properties"]["location_info"] = {}
                        resource["properties"]["location_info"]["vimid"] = vim_id
                        resource["properties"]["location_info"]["tenant"] = tenant

                # if cp_instance_id:
                #     ret = adaptor.get_port_of_vm(self.vim_cache, self.res_cache, vnfd_info, port,
                #                                  self.do_notify_op, "port")
                #     port_info = ignore_case_get(ret, "interfaceAttachment")
                #     net_id = ignore_case_get(port_info, "net_id")
                #     if network_id == net_id:
                #         adaptor.update_port(self.vim_cache, self.res_cache, vnfd_info, port,
                #                             self.do_notify_op, "port")
                #     else:
                #         adaptor.delete_port_of_vm(self.vim_cache, self.res_cache, vnfd_info, port,
                #                                   self.do_notify_op, "port")
                #         adaptor.create_port_of_vm(self.vim_cache, self.res_cache, vnfd_info, port,
                #                                   self.do_notify_op, "port")
                # else:
                adaptor.create_port(self.vim_cache, self.res_cache, vnfd_info, port, self.do_create_port_notify, "port")
                port["port_id"] = self.port_id
                logger.debug('create_port_of_vm request data = %s' % port)
                adaptor.create_port_of_vm(self.vim_cache, self.res_cache, vnfd_info, port,
                                          self.do_notify_op, "port")
                PortInstModel.objects.filter(resourceid=self.port_id).update(vmid=vm_id)
        logger.info('Operate resource complete')

    def send_notification(self):
        data = prepare_notification(nfinstid=self.nf_inst_id,
                                    jobid=self.job_id,
                                    operation=self.op_type,
                                    operation_state=OPERATION_STATE_TYPE.COMPLETED)
        self.set_ext_connectivity(data['changedExtConnectivity'])

        logger.debug('Notify request data = %s' % data)
        NotificationsUtil().send_notification(data)

    def rollback_operation(self):
        pass

    def query_inst_resource(self, inst_resource):
        logger.debug('Query resource begin')
        for resource_type in RESOURCE_MAP.keys():
            resource_table = globals().get(resource_type + 'InstModel')
            resource_insts = resource_table.objects.filter(instid=self.nf_inst_id)
            for resource_inst in resource_insts:
                if not resource_inst.resourceid:
                    continue
                inst_resource[RESOURCE_MAP.get(resource_type)].append(self.get_resource(resource_inst))
        logger.debug('Query resource end, resource=%s' % inst_resource)

    def get_resource(self, resource):
        return {
            "vim_id": resource.vimid,
            "tenant_id": resource.tenant,
            "res_id": resource.resourceid
        }

    def do_create_port_notify(self, res_type, ret):
        self.port_id = ignore_case_get(ret, "id")
        port_save("", self.nf_inst_id, ret)

    def do_notify_op(self, operation_type, status, resid):
        if operation_type == "delete":
            PortInstModel.objects.filter()
            # TODO delete port from table
        elif operation_type == "create":
            pass
            # TODO save port in table
        else:
            pass
            # TODO update port in table
        logger.info('VNF resource %s updated to: %s' % (resid, status))

    def set_ext_connectivity(self, ext_connectivity):
        for extVirtualLink in self.extVirtualLinks:
            vim_connection_id = ignore_case_get(extVirtualLink, "vimConnectionId")
            network_id = ignore_case_get(extVirtualLink, "resourceId")
            ext_cps = ignore_case_get(extVirtualLink, "extCps")
            ext_link_ports = []
            for ext_cp in ext_cps:
                cpd_id = ignore_case_get(ext_cp, "cpdId")
                cp_config = ignore_case_get(ext_cp, "cpConfig")
                cp_instance_id = ignore_case_get(cp_config[0], "cpInstanceId")
                ext_link_ports.append({
                    'id': cp_instance_id,
                    'resourceHandle': {
                        'vimConnectionId': vim_connection_id,
                        'resourceId': self.res_cache.get("port").get(cp_instance_id),
                        'resourceProviderId': cpd_id,
                        'vimLevelResourceType': 'port'
                    },
                    'cpInstanceId': cp_instance_id
                })
            network_resource = {
                'vimConnectionId': vim_connection_id,
                'resourceId': network_id,
                'resourceProviderId': "",
                'vimLevelResourceType': 'network'
            }
            ext_connectivity.append({
                'id': network_id,
                'resourceHandle': network_resource,
                'extLinkPorts': ext_link_ports
            })

    def change_ext_conn_failed_handle(self, error_msg):
        logger.error('Chnage ext conn failed, detail message: %s', error_msg)
        self.vnf_insts.update(status=VNF_STATUS.FAILED,
                              lastuptime=now_time())
        self.lcm_op_occ.notify_lcm(OPERATION_STATE_TYPE.FAILED)
        JobUtil.add_job_status(self.job_id, 255, error_msg)
