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

import json
import logging
import traceback
from threading import Thread

from lcm.pub.database.models import NfInstModel, VmInstModel, VNFCInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.vimapi import adaptor
from lcm.nf.biz.grant_vnf import grant_resource
from lcm.nf.const import VNF_STATUS, GRANT_TYPE, OPERATION_STATE_TYPE, LCM_NOTIFICATION_STATUS
from lcm.nf.const import CHANGE_TYPE, OPERATION_TYPE, HEAL_ACTION_TYPE
from lcm.nf.biz import common
import uuid
from lcm.pub.utils.notificationsutil import NotificationsUtil


logger = logging.getLogger(__name__)


class HealVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(HealVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.affectedvm = ignore_case_get(ignore_case_get(self.data, "additionalParams"), "affectedvm")
        # TODO: Check if we could move the action param into the list of affectedvm structure
        self.action = ignore_case_get(ignore_case_get(self.data, "additionalParams"), "action")
        self.grant_type = ""
        if self.action == HEAL_ACTION_TYPE.START:
            self.grant_type = GRANT_TYPE.HEAL_CREATE
        elif self.action == HEAL_ACTION_TYPE.RESTART:
            self.grant_type = GRANT_TYPE.HEAL_RESTART

    def run(self):
        try:
            self.heal_pre()
            self.lcm_notify(LCM_NOTIFICATION_STATUS.START, OPERATION_STATE_TYPE.STARTING)
            self.apply_grant()
            self.lcm_notify(LCM_NOTIFICATION_STATUS.RESULT, OPERATION_STATE_TYPE.PROCESSING)
            self.heal_resource()
            JobUtil.add_job_status(self.job_id, 100, "Heal Vnf success.")
            NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='INSTANTIATED', lastuptime=now_time())
            self.lcm_notify(LCM_NOTIFICATION_STATUS.RESULT, OPERATION_STATE_TYPE.COMPLETED)
        except NFLCMException as e:
            logger.error(e.message)
            self.lcm_notify(LCM_NOTIFICATION_STATUS.RESULT, OPERATION_STATE_TYPE.FAILED, str(e))
            self.vnf_heal_failed_handle(e.message)
        except Exception as e:
            logger.error(e.message)
            self.lcm_notify(LCM_NOTIFICATION_STATUS.RESULT, OPERATION_STATE_TYPE.FAILED, str(e))
            self.vnf_heal_failed_handle(traceback.format_exc())

    def heal_pre(self):
        if self.action not in (HEAL_ACTION_TYPE.START, HEAL_ACTION_TYPE.RESTART):
            raise NFLCMException("Action should be %s or %s" % (HEAL_ACTION_TYPE.START, HEAL_ACTION_TYPE.RESTART))

        self.vm_id = ignore_case_get(self.affectedvm, "vmid")
        self.vdu_id = ignore_case_get(self.affectedvm, "vduid")
        self.vm_name = ignore_case_get(self.affectedvm, "vmname")
        if not (self.vm_id and self.vdu_id and self.vm_name):
            raise NFLCMException("VM identifiers is not present in request.")

        self.vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        self.vnfd_info = json.loads(self.vnf_insts[0].vnfd_model)

    def apply_grant(self):
        if self.action == HEAL_ACTION_TYPE.RESTART:
            self.vdu = VmInstModel.objects.filter(instid=self.nf_inst_id, resourceid=self.vm_id)
            if not self.vdu:
                raise NFLCMException("VNF Vm(%s) does not exist." % self.vm_id)
            self.vimid = self.vdu[0].vimid
            self.tenant = self.vdu[0].tenant
            logger.debug("Get heal vnf vm(%s,%s) info successfully.", self.vm_id, self.vm_name)
            JobUtil.add_job_status(self.job_id, 20, 'Nf Healing get vnf vm info finish')
            return

        vdus = ignore_case_get(self.vnfd_info, "vdus")
        self.vdu = [elem for elem in vdus if ignore_case_get(elem, "vdu_id") == self.vdu_id]
        if not self.vdu:
            raise NFLCMException("VNF Vdu(%s) does not exist." % self.vdu_id)
        apply_result = grant_resource(data=self.data, nf_inst_id=self.nf_inst_id, job_id=self.job_id,
                                      grant_type=self.grant_type, vdus=self.vdu)

        self.vimid = ignore_case_get(apply_result, "vimid"),
        self.tenant = ignore_case_get(apply_result, "tenant")
        logger.info("Grant resource, response: %s" % apply_result)
        JobUtil.add_job_status(self.job_id, 20, 'Nf Healing grant_resource finish')

    def heal_resource(self):
        logger.info('Heal resource begin')
        data = {'action': self.action, 'vimid': self.vimid, 'tenant': self.tenant}
        adaptor.heal_vim_res(self.vdu, self.vnfd_info, self.do_notify, data, json.loads(self.vnf_insts[0].vimInfo), json.loads(self.vnf_insts[0].resInfo))
        logger.info('Heal resource complete')

    def do_notify(self, res_type, ret):
        logger.info('Creating [%s] resource' % res_type)
        resource_save_method = getattr(common, res_type + '_save')
        resource_save_method(self.job_id, self.nf_inst_id, ret)

    def vnf_heal_failed_handle(self, error_msg):
        logger.error('VNF Healing failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status=VNF_STATUS.FAILED, lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, error_msg)

    def lcm_notify(self, status, opState, err=None):
        notification_content = self.prepareNotificationData(status, opState, err)
        logger.info('Notify data = %s' % notification_content)
        NotificationsUtil().send_notification(notification_content)
        logger.info('Notify end')

    def prepareNotificationData(self, status, opState, err=None):
        affected_vnfcs = []
        if status == LCM_NOTIFICATION_STATUS.RESULT and opState == OPERATION_STATE_TYPE.COMPLETED:
            chtype = ""
            if self.action == HEAL_ACTION_TYPE.START:
                chtype = CHANGE_TYPE.ADDED
            else:
                chtype = CHANGE_TYPE.MODIFIED
            vnfcs = VNFCInstModel.objects.filter(instid=self.nf_inst_id, vmid=self.vm_id)
            vm_resource = {}
            vm = VmInstModel.objects.filter(instid=self.nf_inst_id, resourceid=self.vm_id)
            if vm:
                vm_resource = {
                    'vimConnectionId': vm[0].vimid,
                    'resourceId': vm[0].resourceid,
                    'vimLevelResourceType': 'vm'
                }
            affected_vnfcs.append({
                'id': vnfcs[0].vnfcinstanceid,
                'vduId': vnfcs[0].vduid,
                'changeType': chtype,
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
            "operation": OPERATION_TYPE.HEAL,
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
