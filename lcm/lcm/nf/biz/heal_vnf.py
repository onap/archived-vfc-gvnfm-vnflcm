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

from lcm.pub.database.models import NfInstModel, VmInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.msapi.gvnfmdriver import notify_lcm_to_nfvo, prepare_notification_data
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.vimapi import adaptor
from lcm.nf.biz.grant_vnf import grant_resource
from lcm.nf.const import VNF_STATUS, GRANT_TYPE, HEAL_ACTION_TYPE, CHANGE_TYPE, OPERATION_TYPE
from lcm.nf.biz import common

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
            self.apply_grant()
            self.heal_resource()
            JobUtil.add_job_status(self.job_id, 100, "Heal Vnf success.")
            NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='INSTANTIATED', lastuptime=now_time())
            self.lcm_notify()
        except NFLCMException as e:
            logger.error(e.message)
            self.vnf_heal_failed_handle(e.message)
        except Exception as e:
            logger.error(e.message)
            self.vnf_heal_failed_handle(traceback.format_exc())

    def heal_pre(self):
        if self.action not in (HEAL_ACTION_TYPE.START, HEAL_ACTION_TYPE.RESTART):
            raise NFLCMException("Action type in Request in invalid. Should be %s or %s" % (HEAL_ACTION_TYPE.START, HEAL_ACTION_TYPE.RESTART))

        self.vm_id = ignore_case_get(self.affectedvm, "vmid")
        self.vdu_id = ignore_case_get(self.affectedvm, "vduid")
        self.vm_name = ignore_case_get(self.affectedvm, "vmname")
        if not (self.vm_id and self.vdu_id and self.vm_name):
            raise NFLCMException("VM identifiers is not present in request.")

        self.vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        self.vnfd_info = json.loads(self.vnf_insts[0].vnfd_model)

    def apply_grant(self):
        if self.action == HEAL_ACTION_TYPE.RESTART:
            self.vdu = VmInstModel.objects.filter(instid=self.nf_inst_id, is_predefined=1, vmid=self.vm_id, vmname=self.vm_name)
            if not self.vdu:
                raise NFLCMException("VNF Vm does not exist.")
            self.vimid = self.vdu[0].vimid
            self.tenant = self.vdu[0].tenant
        elif self.action == HEAL_ACTION_TYPE.START:
            vdus = ignore_case_get(self.vnfd_info, "vdus")
            self.vdu = [elem for elem in vdus if ignore_case_get(elem, "vdu_id") == self.vdu_id]
            if not self.vdu:
                raise NFLCMException("VNF Vm does not exist.")
        apply_result = grant_resource(data=self.data, nf_inst_id=self.nf_inst_id, job_id=self.job_id,
                                      grant_type=self.grant_type, vdus=self.vdu)
        if self.action == HEAL_ACTION_TYPE.START:
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

    def lcm_notify(self):
        notification_content = prepare_notification_data(self.nf_inst_id, self.job_id, CHANGE_TYPE.MODIFIED, OPERATION_TYPE.HEAL)
        logger.info('Notify request data = %s' % notification_content)
        resp = notify_lcm_to_nfvo(json.dumps(notification_content))
        logger.info('Lcm notify end, response %s' % resp)

    def vnf_heal_failed_handle(self, error_msg):
        logger.error('VNF Healing failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status=VNF_STATUS.FAILED, lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, error_msg)
