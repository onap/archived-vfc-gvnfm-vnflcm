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

from lcm.nf.biz.grant_vnf import grant_resource
from lcm.nf.const import GRANT_TYPE, CHANGE_TYPE
from lcm.nf.const import OPERATION_TYPE, OPERATION_TASK
from lcm.pub.utils.notificationsutil import NotificationsUtil
from lcm.pub.utils.notificationsutil import prepare_notification_data
from lcm.pub.utils.values import ignore_case_get
from .opt_vnf_base import OptVnfBase

logger = logging.getLogger(__name__)


class ChangeVnfFlavour(OptVnfBase):
    def __init__(self, data, nf_inst_id, job_id):
        super(ChangeVnfFlavour, self).__init__(data=data,
                                               nf_inst_id=nf_inst_id,
                                               job_id=job_id,
                                               op_type=OPERATION_TYPE.CHANGE_FLAVOUR,
                                               op_task=OPERATION_TASK.CHANGE_FLAVOUR)

    def pre_operation(self):
        self.vnfd_info = {}  # TODO

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
        pass

    def send_notification(self):
        data = prepare_notification_data(nfinstid=self.nf_inst_id,
                                         jobid=self.job_id,
                                         changetype=CHANGE_TYPE.MODIFIED,
                                         operation=self.op_type)
        logger.debug('Notify request data = %s' % data)
        NotificationsUtil().send_notification(data)

    def rollback_operation(self):
        pass
