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
from threading import Thread

from lcm.pub.database.models import NfInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.nf.const import OPERATION_STATE_TYPE
from lcm.nf.const import OPERATION_TYPE
from lcm.nf.const import OPERATION_TASK
from lcm.pub.utils.notificationsutil import NotificationsUtil
from lcm.pub.utils.notificationsutil import prepare_notification
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from .operate_vnf_lcm_op_occ import VnfLcmOpOcc

logger = logging.getLogger(__name__)


class UpdateVnf(Thread):
    def __init__(self, data, instanceid, job_id):
        super(UpdateVnf, self).__init__()
        self.data = data
        self.nf_inst_id = instanceid
        self.job_id = job_id
        self.vnf_insts = NfInstModel.objects.filter(nfinstid=instanceid)
        self.lcm_op_occ = VnfLcmOpOcc(
            vnf_inst_id=instanceid,
            lcm_op_id=job_id,
            operation=OPERATION_TYPE.MODIFY_INFO,
            task=OPERATION_TASK.MODIFY
        )

    def run(self):
        logger.debug("start update for vnf %s", self.nf_inst_id)
        key = "vnfInstanceName"
        try:
            self.lcm_op_occ.notify_lcm(OPERATION_STATE_TYPE.PROCESSING)
            JobUtil.add_job_status(self.job_id, 50, "Start updating VNF.")

            if key in self.data and self.data[key] is not None:
                self.vnf_insts.update(nf_name=self.data[key],
                                      lastuptime=now_time())

            key = "vnfInstanceDescription"
            if key in self.data and self.data[key] is not None:
                self.vnf_insts.update(nf_desc=self.data[key],
                                      lastuptime=now_time())

            key = "vnfPkgId"
            if key in self.data:
                self.vnf_insts.update(vnfdid=self.data[key],
                                      lastuptime=now_time())

            JobUtil.add_job_status(self.job_id, 75, "Start sending notification.")
            self.send_notification()

            JobUtil.add_job_status(self.job_id, 100, "Update VNF success.")
        except NFLCMException as e:
            logger.error(e.message)
            self.lcm_op_occ.notify_lcm(OPERATION_STATE_TYPE.FAILED, e.message)
            JobUtil.add_job_status(self.job_id, 255, e.message)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            self.lcm_op_occ.notify_lcm(OPERATION_STATE_TYPE.FAILED, e.message)
            JobUtil.add_job_status(self.job_id, 255, e.message)

    def send_notification(self):
        notify_data = prepare_notification(nfinstid=self.nf_inst_id,
                                           jobid=self.job_id,
                                           operation=OPERATION_TYPE.MODIFY_INFO,
                                           operation_state=OPERATION_STATE_TYPE.COMPLETED)

        notify_data["changedInfo"] = {}
        for key in ("vnfInstanceName", "vnfInstanceDescription"):
            if key in self.data and self.data[key] is not None:
                notify_data["changedInfo"][key] = self.data[key]

        logger.debug('Notification data: %s' % notify_data)
        NotificationsUtil().send_notification(notify_data)
