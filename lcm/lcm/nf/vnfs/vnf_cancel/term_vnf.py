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
import traceback
from threading import Thread

from lcm.pub.database.models import JobStatusModel, NfInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class TermVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(TermVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.terminationType = ignore_case_get(self.data, "terminationType")
        self.gracefulTerminationTimeout = ignore_case_get(self.data, "gracefulTerminationTimeout")

    def run(self):
        try:
            self.term_pre()
            JobUtil.add_job_status(self.job_id, 100, "Terminate Vnf success.")
            is_exist = JobStatusModel.objects.filter(jobid=self.job_id).exists()
            logger.debug("check_ns_inst_name_exist::is_exist=%s" % is_exist)
        except NFLCMException as e:
            logger.error('VNF instantiation failed, detail message: %s' % e.message)
            # NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='failed', lastuptime=now_time())
            JobUtil.add_job_status(self.job_id, 255, e.message)
            # self.vnf_term_failed_handle(e.message)
        except:
            # self.vnf_term_failed_handle('unexpected exception')
            logger.error(traceback.format_exc())

    def term_pre(self):
        vnf_insts = NfInstModel.objects.filter(pk=self.nf_inst_id)
        if not vnf_insts.exists():
            raise NFLCMException('VnfInst(%s) does not exist' % self.nf_inst_id)
        sel_vnf = vnf_insts[0]
        if sel_vnf.instantiationState != 'VNF_INSTANTIATED':
            raise NFLCMException("No instantiated vnf")
        if self.terminationType == 'GRACEFUL' and not self.gracefulTerminationTimeout:
            raise NFLCMException("Graceful termination must set timeout")
        JobUtil.add_job_status(self.job_id, 10, 'Nf terminating pre-check finish')
        logger.info("Nf terminating pre-check finish")