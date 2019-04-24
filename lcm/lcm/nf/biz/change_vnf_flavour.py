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

import logging
import traceback
import json
from threading import Thread

from lcm.nf.biz.grant_vnf import grant_resource
from lcm.nf.const import GRANT_TYPE, CHANGE_TYPE
from lcm.nf.const import VNF_STATUS
from lcm.nf.const import OPERATION_TYPE, OPERATION_TASK
from lcm.nf.const import OPERATION_STATE_TYPE
from lcm.pub.utils.notificationsutil import NotificationsUtil, prepare_notification_data
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.exceptions import NFLCMException
from lcm.pub.database.models import NfInstModel
from .operate_vnf_lcm_op_occ import VnfLcmOpOcc

logger = logging.getLogger(__name__)


class ChangeVnfFlavour(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(ChangeVnfFlavour, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        self.lcm_op_occ = VnfLcmOpOcc(
            vnf_inst_id=nf_inst_id,
            lcm_op_id=job_id,
            operation=OPERATION_TYPE.CHANGE_FLAVOUR,
            task=OPERATION_TASK.CHANGE_FLAVOUR
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
                                   "Start to change vnf flavour.")
            self.do_operation()
            self.vnf_insts.update(
                status='INSTANTIATED',
                lastuptime=now_time()
            )
            self.send_notification()
            JobUtil.add_job_status(self.job_id,
                                   100,
                                   "Change vnf flavour success.")
        except NFLCMException as e:
            logger.error(e.message)
            self.change_vnf_flavour_failed_handle(e.message)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            self.change_vnf_flavour_failed_handle(e.message)

    def apply_grant(self):
        logger.debug("Start change flavour apply grant")
        vdus = ignore_case_get(self.vnfd_info, "vdus")
        grant_result = grant_resource(data=self.data,
                                      nf_inst_id=self.nf_inst_id,
                                      job_id=self.job_id,
                                      grant_type=GRANT_TYPE.CHANGE_FLAVOUR,
                                      vdus=vdus)
        logger.debug("Change flavour Grant result: %s", grant_result)

    def do_operation(self):
        logger.info('Operation resource begin')
        self.vnfd_info = json.loads(self.vnf_insts[0].vnfd_model)
        # TODO: Add operation logic

    def send_notification(self):
        data = prepare_notification_data(nfinstid=self.nf_inst_id,
                                         jobid=self.job_id,
                                         changetype=CHANGE_TYPE.MODIFIED,
                                         operation=OPERATION_TYPE.CHANGE_FLAVOUR)
        logger.debug('Notify request data = %s' % data)
        NotificationsUtil().send_notification(data)

    def change_vnf_flavour_failed_handle(self, error_msg):
        logger.error('Chnage vnf flavour failed, detail message: %s', error_msg)
        self.vnf_insts.update(status=VNF_STATUS.FAILED,
                              lastuptime=now_time())
        self.lcm_op_occ.notify_lcm(OPERATION_STATE_TYPE.FAILED, error_msg)
        JobUtil.add_job_status(self.job_id, 255, error_msg)
