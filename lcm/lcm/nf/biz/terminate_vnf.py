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

import json
import logging
import traceback
from threading import Thread

from lcm.nf.const import VNF_STATUS, RESOURCE_MAP
from lcm.pub.database.models import (
    NfInstModel, VmInstModel, NetworkInstModel,
    StorageInstModel, PortInstModel, VNFCInstModel,
    FlavourInstModel, SubNetworkInstModel
)
from lcm.pub.exceptions import NFLCMException
from lcm.pub.msapi.gvnfmdriver import (
    apply_grant_to_nfvo,
    notify_lcm_to_nfvo,
    prepare_notification_data
)
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.vimapi import adaptor

logger = logging.getLogger(__name__)


class TerminateVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(TerminateVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.terminationType = ignore_case_get(self.data, "terminationType")
        self.gracefulTerminationTimeout = ignore_case_get(self.data, "gracefulTerminationTimeout")
        self.inst_resource = {'volumn': [], 'network': [], 'subnet': [], 'port': [], 'flavor': [], 'vm': []}

    def run(self):
        try:
            if self.term_pre():
                self.grant_resource()
                self.query_inst_resource()
                self.query_notify_data()
                self.delete_resource()
                self.lcm_notify()
            JobUtil.add_job_status(self.job_id, 100, "Terminate Vnf success.")
        except NFLCMException as e:
            self.vnf_term_failed_handle(e.message)
        except Exception as e:
            logger.error(e.message)
            self.vnf_term_failed_handle(traceback.format_exc())

    def term_pre(self):
        vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if not vnf_insts.exists():
            logger.warn('VnfInst(%s) does not exist' % self.nf_inst_id)
            return False
        if self.terminationType == 'GRACEFUL' and not self.gracefulTerminationTimeout:
            logger.warn("Set Graceful default termination timeout = 60")
            self.gracefulTerminationTimeout = 60
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status=VNF_STATUS.TERMINATING)
        JobUtil.add_job_status(self.job_id, 10, 'Nf terminating pre-check finish')
        logger.info("Nf terminating pre-check finish")
        return True

    def grant_resource(self):
        logger.info("Grant resource begin")
        content_args = {
            'vnfInstanceId': self.nf_inst_id,
            'vnfDescriptorId': '',
            'lifecycleOperation': 'Terminate',
            'jobId': self.job_id,
            'addResource': [],
            'removeResource': [],
            'placementConstraint': [],
            'additionalParam': {}
        }

        vdus = VmInstModel.objects.filter(instid=self.nf_inst_id, is_predefined=1)
        res_index = 1
        for vdu in vdus:
            res_def = {
                'type': 'VDU',
                'resDefId': str(res_index),
                'resDesId': vdu.resouceid}
            content_args['removeResource'].append(res_def)
            res_index += 1

        vnfInsts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        content_args['additionalParam']['vnfmid'] = vnfInsts[0].vnfminstid
        content_args['additionalParam']['vimid'] = vdus[0].vimid
        logger.info('Grant request data=%s' % content_args)
        self.apply_result = apply_grant_to_nfvo(json.dumps(content_args))
        logger.info("Grant resource end, response: %s" % self.apply_result)
        JobUtil.add_job_status(self.job_id, 20, 'Nf terminating grant_resource finish')

    def query_inst_resource(self):
        logger.info('Query resource begin')
        for resource_type in RESOURCE_MAP.keys():
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
            "res_id": resource.resouceid,
            "is_predefined": resource.is_predefined
        }

    def query_notify_data(self):
        self.notify_data = prepare_notification_data(self.nf_inst_id, self.job_id, "RMOVED")
        NetworkInstModel.objects.filter(instid=self.nf_inst_id)
        StorageInstModel.objects.filter(instid=self.nf_inst_id)
        PortInstModel.objects.filter(instid=self.nf_inst_id)
        VNFCInstModel.objects.filter(instid=self.nf_inst_id)
        FlavourInstModel.objects.filter(instid=self.nf_inst_id)
        SubNetworkInstModel.objects.filter(instid=self.nf_inst_id)

    def delete_resource(self):
        logger.info('Rollback resource begin')
        adaptor.delete_vim_res(self.inst_resource, self.do_notify_delete)
        logger.info('Rollback resource complete')

    def do_notify_delete(self, res_type, res_id):
        logger.error('Deleting [%s] resource, resourceid [%s]' % (res_type, res_id))
        resource_type = RESOURCE_MAP.keys()[RESOURCE_MAP.values().index(res_type)]
        resource_table = globals().get(resource_type + 'InstModel')
        resource_table.objects.filter(instid=self.nf_inst_id, resouceid=res_id).delete()

    def lcm_notify(self):
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='NOT_INSTANTIATED', lastuptime=now_time())
        logger.info('Send notify request to nfvo')
        resp = notify_lcm_to_nfvo(json.dumps(self.notify_data))
        logger.info('Lcm notify end, response: %s' % resp)

    def vnf_term_failed_handle(self, error_msg):
        logger.error('VNF termination failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='failed', lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, error_msg)
