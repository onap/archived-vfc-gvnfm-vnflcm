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

from lcm.pub.database.models import NfInstModel, NfvoRegInfoModel

logger = logging.getLogger(__name__)


class DeleteVnf:
    def __init__(self, data, instanceid):
        self.data = data
        self.nf_inst_id = instanceid

    def do_biz(self):
            self.check_parameter()
            self.delete_info_from_db()
            logger.debug('VnfInst(%s) is deleted.' % self.nf_inst_id)

    def check_parameter(self):
        vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if not vnf_insts.exists():
            logger.warn('VnfInst(%s) does not exist' % self.nf_inst_id)

    def delete_info_from_db(self):
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).delete()
        NfvoRegInfoModel.objects.filter(nfvoid=self.nf_inst_id).delete()
