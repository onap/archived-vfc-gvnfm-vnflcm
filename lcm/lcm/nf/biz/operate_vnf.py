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
from lcm.nf.const import VNF_STATUS, RESOURCE_MAP, GRANT_TYPE

logger = logging.getLogger(__name__)


class OperateVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(OperateVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.grant_type = GRANT_TYPE.OPERATE
        self.changeStateTo = ignore_case_get(self.data, "changeStateTo")
        self.stopType = ignore_case_get(self.data, "stopType")
        self.gracefulStopTimeout = ignore_case_get(self.data, "gracefulStopTimeout")
        self.inst_resource = {'vm': []}

    def run(self):
        try:
            self.apply_grant()
            self.query_inst_resource()
            self.operate_resource()
            JobUtil.add_job_status(self.job_id, 100, "Operate Vnf success.")
            NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='INSTANTIATED', lastuptime=now_time(), operationState=self.changeStateTo)
            self.lcm_notify()
        except NFLCMException as e:
            self.vnf_operate_failed_handle(e.message)
        except Exception as e:
            logger.error(e.message)
            self.vnf_operate_failed_handle(traceback.format_exc())

    def apply_grant(self):
        vdus = VmInstModel.objects.filter(instid=self.nf_inst_id, is_predefined=1)
        apply_result = grant_resource(data=self.data, nf_inst_id=self.nf_inst_id, job_id=self.job_id,
                                      grant_type=self.grant_type, vdus=vdus)
        logger.info("Grant resource, response: %s" % apply_result)
        JobUtil.add_job_status(self.job_id, 20, 'Nf Operate grant_resource finish')

    def query_inst_resource(self):
        logger.info('Query resource begin')
        # Querying only vm resources now
        resource_type = "Vm"
        resource_table = globals().get(resource_type + 'InstModel')
        resource_insts = resource_table.objects.filter(instid=self.nf_inst_id)
        for resource_inst in resource_insts:
            if not resource_inst.resouceid:
                continue
            self.inst_resource[RESOURCE_MAP.get(resource_type)].append(self.get_resource(resource_inst))
        logger.info('Query resource end, resource=%s' % self.inst_resource)

    def get_resource(self, resource):
        return {
            "vim_id": resource.vimid,
            "tenant_id": resource.tenant,
            "id": resource.resouceid
        }

    def operate_resource(self):
        logger.info('Operate resource begin')
        adaptor.operate_vim_res(self.inst_resource, self.changeStateTo, self.stopType, self.gracefulStopTimeout, self.do_notify_op)
        logger.info('Operate resource complete')

    def lcm_notify(self):
        notification_content = prepare_notification_data(self.nf_inst_id, self.job_id, "MODIFIED")
        logger.info('Notify request data = %s' % notification_content)
        resp = notify_lcm_to_nfvo(json.dumps(notification_content))
        logger.info('Lcm notify end, response %s' % resp)

    def vnf_operate_failed_handle(self, error_msg):
        logger.error('VNF Operation failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status=VNF_STATUS.FAILED, lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, error_msg)

    def do_notify_op(self, status, resid):
        logger.error('VNF resource %s updated to: %s' % (resid, status))
        VmInstModel.objects.filter(instid=self.nf_inst_id, resouceid=resid).update(operationalstate=status)
