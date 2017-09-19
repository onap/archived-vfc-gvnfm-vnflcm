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

from lcm.pub.config.config import REPORT_TO_AAI
from lcm.pub.database.models import NfInstModel, NfvoRegInfoModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.msapi.aai import query_vnf_aai, delete_vnf_aai

logger = logging.getLogger(__name__)


class DeleteVnf:
    def __init__(self, data, instanceid):
        self.data = data
        self.nf_inst_id = instanceid

    def do_biz(self):
        try:
            self.check_parameter()
            self.delete_info_from_db()
            if REPORT_TO_AAI:
                self.delete_vnf_in_aai()
        except NFLCMException as e:
            logger.debug('Delete VNF instance[%s] from AAI failed' % self.nf_inst_id)
        except:
            logger.debug('Delete VNF instance[%s] failed' % self.nf_inst_id)

    def check_parameter(self):
        vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if not vnf_insts.exists():
            logger.warn('VnfInst(%s) does not exist' % self.nf_inst_id)
            return
            # sel_vnf = vnf_insts[0]
            # if sel_vnf.status != 'NOT_INSTANTIATED':
            #    raise NFLCMException("Don't allow to delete vnf(status:[%s])" % sel_vnf.status)

    def delete_info_from_db(self):
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).delete()
        NfvoRegInfoModel.objects.filter(nfvoid=self.nf_inst_id).delete()

    def delete_vnf_in_aai(self):
        logger.debug("DeleteVnf::delete_vnf_in_aai::delete vnf instance[%s] in aai." % self.nf_inst_id)

        # query vnf instance in aai, get resource_version
        customer_info = query_vnf_aai(self.nf_inst_id)
        resource_version = customer_info["resource-version"]

        # delete vnf instance from aai
        resp_data, resp_status = delete_vnf_aai(self.nf_inst_id, resource_version)
        if resp_data:
            logger.debug("Fail to delete vnf instance[%s] from aai, resp_status: [%s]." % (self.nf_inst_id, resp_status))
        else:
            logger.debug(
                "Success to delete vnf instance[%s] from aai, resp_status: [%s]." % (self.nf_inst_id, resp_status))
