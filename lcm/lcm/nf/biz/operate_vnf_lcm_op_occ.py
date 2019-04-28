# Copyright (C) 2019 ZTE. All Rights Reserved
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
from multiprocessing import Lock

from lcm.nf import const
from lcm.pub.database.models import VNFLcmOpOccModel
from lcm.pub.exceptions import NFLCMExceptionNotFound
from lcm.pub.utils.notificationsutil import NotificationsUtil
from lcm.pub.utils.notificationsutil import prepare_notification
from lcm.pub.utils.timeutil import now_time

logger = logging.getLogger(__name__)

MUTEX_UPD_OCC = Lock()


"""
operation: INSTANTIATE, SCALE, SCALE_TO_LEVEL, CHANGE_FLAVOUR,
           TERMINATE, HEAL, OPERATE, CHANGE_EXT_CONN, MODIFY_INFO
task: instantiate, scale, scale_to_level, change_flavour
      operate, heal, change_ext_conn, terminate
operation_state: STARTING, PROCESSING, COMPLETED, FAILED_TEMP,
                 FAILED, ROLLING_BACK, ROLLED_BACK
"""


class VnfLcmOpOcc:
    def __init__(self, vnf_inst_id, lcm_op_id, operation, task):
        self.vnf_inst_id = vnf_inst_id
        self.lcm_op_id = lcm_op_id
        self.operation = operation
        self.task = task

    def add(self):
        href_params = {
            "id": self.vnf_inst_id,
            "task": self.task,
            "prefix": const.URL_PREFIX
        }
        href = "%(prefix)s/vnf_instances/%(id)s/%(task)s" % href_params
        if href.endswith("/"):
            href = href[:-1]
        VNFLcmOpOccModel(id=self.lcm_op_id,
                         operation_state=const.OPERATION_STATE_TYPE.STARTING,
                         state_entered_time=now_time(),
                         start_time=now_time(),
                         vnf_instance_id=self.vnf_inst_id,
                         grant_id=None,
                         operation=self.operation,
                         is_automatic_invocation=False,
                         operation_params='{}',
                         is_cancel_pending=False,
                         cancel_mode=None,
                         error=None,
                         resource_changes=None,
                         changed_ext_connectivity=None,
                         links=json.dumps({
                             "self": {
                                 "href": href
                             },
                             "vnfInstance": {
                                 "href": self.vnf_inst_id
                             }
                         })).save()

    def upd(self, operation_state=None, sub_operation=None, error=None):
        occ = VNFLcmOpOccModel.objects.filter(id=self.lcm_op_id)
        with MUTEX_UPD_OCC:
            if operation_state:
                occ.update(operation_state=operation_state)
            if sub_operation:
                occ.update(sub_operation=sub_operation)
            if error:
                occ.update(error=json.dumps(error))

    def get(self):
        lcm_op_occ_obj = VNFLcmOpOccModel.objects.filter(id=self.lcm_op_id).first()
        if not lcm_op_occ_obj:
            raise NFLCMExceptionNotFound('Occurrence(%s) does not exist.' % self.lcm_op_id)
        return lcm_op_occ_obj

    def notify_lcm(self, operation_state, error=''):
        data = prepare_notification(nfinstid=self.vnf_inst_id,
                                    jobid=self.lcm_op_id,
                                    operation=self.operation,
                                    operation_state=operation_state)
        if error:
            data['error'] = error

        logger.debug('Notification data: %s' % data)
        return NotificationsUtil().send_notification(data)
