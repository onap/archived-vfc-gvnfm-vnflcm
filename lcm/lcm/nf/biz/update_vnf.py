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
from threading import Thread

from lcm.pub.database.models import NfInstModel
from lcm.nf.const import OPERATION_STATE_TYPE
from lcm.nf.const import OPERATION_TYPE
from lcm.pub.utils.notificationsutil import NotificationsUtil
from lcm.pub.utils.notificationsutil import prepare_notification
from lcm.pub.utils.timeutil import now_time

logger = logging.getLogger(__name__)


class UpdateVnf(Thread):
    def __init__(self, data, instanceid, job_id):
        self.data = data
        self.nf_inst_id = instanceid
        self.job_id = job_id
        self.vnf_insts = NfInstModel.objects.filter(nfinstid=instanceid)

    def run(self):
        logger.debug("start update for vnf %s", self.nf_inst_id)
        key = "vnfInstanceName"
        if key in self.data and self.data[key] != None:
            self.vnf_insts.update(nf_name=self.data[key],
                                  lastuptime=now_time())

        key = "vnfInstanceDescription"
        if key in self.data and self.data[key] != None:
            self.vnf_insts.update(nf_desc=self.data[key],
                                  lastuptime=now_time())

        key = "vnfPkgId"
        if key in self.data:
            self.vnf_insts.update(vnfdid=self.data[key],
                                  lastuptime=now_time())

    def send_notification(self):
        notify_data = prepare_notification(nfinstid=self.nf_inst_id,
                                           jobid=self.job_id,
                                           operation=OPERATION_TYPE.MODIFY_INFO,
                                           operation_state=OPERATION_STATE_TYPE.COMPLETED)

        notify_data["changedInfo"] = {}
        for key in ("vnfInstanceName", "vnfInstanceDescription"):
            if key in self.data and self.data[key] != None:
                notify_data["changedInfo"][key] = self.data[key]

        logger.debug('Notification data: %s' % notify_data)
        NotificationsUtil().send_notification(notify_data)
