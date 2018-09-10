# Copyright (C) 2018 Verizon. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import json
import logging
import traceback
from threading import Thread

from lcm.pub.database.models import NfInstModel, VmInstModel, VNFCInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.notificationsutil import NotificationsUtil
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.vimapi import adaptor
from lcm.nf.biz.grant_vnf import grant_resource
from lcm.nf.const import VNF_STATUS, RESOURCE_MAP, GRANT_TYPE, OPERATION_STATE_TYPE, LCM_NOTIFICATION_STATUS, CHANGE_TYPE, OPERATION_TYPE
import uuid

logger = logging.getLogger(__name__)


class OperateVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(OperateVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.grant_type = GRANT_TYPE.OPERATE
        self.changeStateTo = ignore_case_get(self.data, "changeStateTo")
        self.stopType = ignore_case_get(self.data, "stopType")
        self.gracefulStopTimeout = ignore_case_get(self.data, "gracefulStopTimeout")
        self.inst_resource = {'vm': []}

    def run(self):
        try:
            self.lcm_notify(LCM_NOTIFICATION_STATUS.START, OPERATION_STATE_TYPE.STARTING)
            self.apply_grant()
            self.query_inst_resource()
            self.lcm_notify(LCM_NOTIFICATION_STATUS.RESULT, OPERATION_STATE_TYPE.PROCESSING)
            self.operate_resource()
            JobUtil.add_job_status(self.job_id, 100, "Operate Vnf success.")
            NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='INSTANTIATED', lastuptime=now_time())
            self.lcm_notify(LCM_NOTIFICATION_STATUS.RESULT, OPERATION_STATE_TYPE.COMPLETED)
        except NFLCMException as e:
            self.lcm_notify(LCM_NOTIFICATION_STATUS.RESULT, OPERATION_STATE_TYPE.FAILED, str(e))
            self.vnf_operate_failed_handle(e.message)
        except Exception as e:
            logger.error(e.message)
            self.lcm_notify(LCM_NOTIFICATION_STATUS.RESULT, OPERATION_STATE_TYPE.FAILED, str(e))
            self.vnf_operate_failed_handle(traceback.format_exc())

    def apply_grant(self):
        vdus = VmInstModel.objects.filter(instid=self.nf_inst_id)
        apply_result = grant_resource(data=self.data, nf_inst_id=self.nf_inst_id, job_id=self.job_id,
                                      grant_type=self.grant_type, vdus=vdus)
        logger.info("Grant resource, response: %s" % apply_result)
        JobUtil.add_job_status(self.job_id, 20, 'Nf Operate grant_resource finish')

    def query_inst_resource(self):
        logger.info('Query resource begin')
        # Querying only vm resources now
        resource_type = "Vm"
        resource_table = globals().get(resource_type + 'InstModel')
        resource_insts = resource_table.objects.filter(instid=self.nf_inst_id)
        for resource_inst in resource_insts:
            if not resource_inst.resourceid:
                continue
            self.inst_resource[RESOURCE_MAP.get(resource_type)].append(self.get_resource(resource_inst))
        logger.info('Query resource end, resource=%s' % self.inst_resource)

    def get_resource(self, resource):
        return {
            "vim_id": resource.vimid,
            "tenant_id": resource.tenant,
            "id": resource.resourceid
        }

    def operate_resource(self):
        logger.info('Operate resource begin')
        adaptor.operate_vim_res(self.inst_resource, self.changeStateTo, self.stopType, self.gracefulStopTimeout, self.do_notify_op)
        logger.info('Operate resource complete')

    def lcm_notify(self, status, opState, err=None):
        notification_content = self.prepareNotificationData(status, opState, err)
        logger.info('Notify data = %s' % notification_content)
        NotificationsUtil().send_notification(notification_content)
        logger.info('Notify end')

    def vnf_operate_failed_handle(self, error_msg):
        logger.error('VNF Operation failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status=VNF_STATUS.FAILED, lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, error_msg)

    def do_notify_op(self, status, resid):
        logger.error('VNF resource %s updated to: %s' % (resid, status))

    def prepareNotificationData(self, status, opState, err=None):
        affected_vnfcs = []
        if status == LCM_NOTIFICATION_STATUS.RESULT and opState == OPERATION_STATE_TYPE.COMPLETED:
            vnfcs = VNFCInstModel.objects.filter(instid=self.nf_inst_id)
            for vnfc in vnfcs:
                vm_resource = {}
                if vnfc.vmid:
                    vm = VmInstModel.objects.filter(vmid=vnfc.vmid)
                    if vm:
                        vm_resource = {
                            'vimConnectionId': vm[0].vimid,
                            'resourceId': vm[0].resourceid,
                            'vimLevelResourceType': 'vm'
                        }
                affected_vnfcs.append({
                    'id': vnfc.vnfcinstanceid,
                    'vduId': vnfc.vduid,
                    'changeType': CHANGE_TYPE.MODIFIED,
                    'computeResource': vm_resource
                })
        notification_content = {
            "id": str(uuid.uuid4()),
            "notificationType": "VnfLcmOperationOccurrenceNotification",
            "subscriptionId": "",
            "timeStamp": now_time(),
            "notificationStatus": status,
            "operationState": opState,
            "vnfInstanceId": self.nf_inst_id,
            "operation": OPERATION_TYPE.OPERATE,
            "isAutomaticInvocation": "false",
            "vnfLcmOpOccId": self.job_id,
            "affectedVnfcs": affected_vnfcs,
            "affectedVirtualLinks": [],
            "affectedVirtualStorages": [],
            "changedInfo": {},
            "changedExtConnectivity": [],
            "_links": {"vnfInstance": {"href": ""},
                       "subscription": {"href": ""},
                       "vnfLcmOpOcc": {"href": ""}}
        }
        if opState in (OPERATION_STATE_TYPE.FAILED, OPERATION_STATE_TYPE.FAILED_TEMP):
            notification_content["error"] = {"status": 500, "detail": err}
        notification_content["_links"]["vnfInstance"]["href"] = "/vnf_instances/%s" % self.nf_inst_id
        notification_content["_links"]["vnfLcmOpOcc"]["href"] = "/vnf_lc_ops/%s" % self.job_id
        return notification_content
