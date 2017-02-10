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

from lcm.pub.database.models import NfInstModel, JobStatusModel, NfvoRegInfoModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.msapi.nfvolcm import vnfd_rawdata_get, apply_grant_to_nfvo
from lcm.pub.utils.jobutil import JobUtil

logger = logging.getLogger(__name__)


class InstVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(InstVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.nfvo_inst_id = ''
        self.vnfm_inst_id = ''


    def run(self):
        try:
            self.inst_pre(self.nf_inst_id)

            self.apply_grant()

            # self.apply_res(args)
            # self.check_res_status(args)
            # self.wait_inst_finish(args)
            # self.lcm_notify(args)
            JobUtil.add_job_status(self.job_id, 100, "Instantiate Vnf success.")
            is_exist = JobStatusModel.objects.filter(jobid=self.job_id).exists()
            logger.debug("check_ns_inst_name_exist::is_exist=%s" % is_exist)
        except NFLCMException as e:
            self.inst_exception(e.message)
            pass
        except Exception:
            logger.error(traceback.format_exc())
            self.inst_exception('unexpected exception')

    def inst_pre(self, args):
        logger.info('inst_pre, args=%s' % args)
        is_exist = NfInstModel.objects.filter(nfinstid=self.nf_inst_id).exists()
        logger.debug("check_ns_inst_name_exist::is_exist=%s" % is_exist)
        if not is_exist:
            logger.error("VNF nf_inst_id is not exist.")
            JobUtil.add_job_status(self.job_id, 255, "VNF nf_inst_id is not exist.")
            raise NFLCMException('VNF nf_inst_id is not exist.')

        vnf_inst = NfInstModel.objects.get(nfinstid=self.nf_inst_id)
        self.vnfm_inst_id = vnf_inst.vnfm_inst_id
        if vnf_inst.instantiationState != 'NOT_INSTANTIATED':
            logger.error("VNF instantiationState is not NOT_INSTANTIATED.")
            JobUtil.add_job_status(self.job_id, 255, "VNF instantiationState is not NOT_INSTANTIATED.")
            raise NFLCMException('VNF instantiationState is not NOT_INSTANTIATED.')

        #get rawdata by vnfd_id
        ret = vnfd_rawdata_get(vnf_inst.vnfdid)
        if ret[0] != 0:
            raise NFLCMException("Get vnfd_raw_data failed.")
        self.vnfd_info = json.JSONDecoder().decode(ret[1])
        #checkParameterExist
        for cp in self.data:
            if cp not in self.vnfd_info:
                logger.error("[%s] is not defined in vnfd_info."%cp)
                JobUtil.add_job_status(self.job_id, 255, "Input parameter is not defined in vnfd_info.")
                raise NFLCMException('Input parameter is not defined in vnfd_info.')
        #get nfvo info
        JobUtil.add_job_status(self.job_id, 5, 'GET_NFVO_CONNECTION_INFO')
        self.load_nfvo_config()

    def apply_grant(self):
        logger.info('[NF instantiation] send resource grand request to nfvo start')
        #self.check_vm_capacity()
        content_args = {'nfvoInstanceId': self.nfvo_inst_id, 'vnfmInstanceId': self.vnfm_inst_id,
                        'nfInstanceId': self.nf_inst_id, 'nfDescriptorId': '',
                        'lifecycleOperation': 'Instantiate', 'jobId': self.job_id, 'addResource': [],
                        'removeResource': [], 'placementConstraint': [], 'exVimIdList': [], 'additionalParam': {}}

        vdus = self.vnfd_info['vdus']
        res_index = 1
        for vdu in vdus:
            res_def = {'type': 'VDU', 'resourceDefinitionId': str(res_index), 'vduId': vdu['vdu_id'],
                       'vimid': '', 'tenant': ''}
            if self.vnfd_info['metadata']['cross_dc']:
                res_def['vimid'] = vdu['properties']['location_info']['vimId']
                res_def['tenant'] = vdu['properties']['location_info']['tenant']
            content_args['addResource'].append(res_def)
            res_index += 1
        logger.info('content_args=%s' % content_args)
        resp = apply_grant_to_nfvo(content_args)
        logger.info("[NF instantiation] get grant response = %s" % resp)
        if resp[0] != 0:
            err_msg = str(resp[1])
            logger.error("Nf instancing apply grant exception.[%s]" % err_msg)
            JobUtil.add_job_status(self.job_id, 255, 'Nf instancing apply grant exception')
            raise NFLCMException('Nf instancing apply grant exception')

        #update_resources_table()
        JobUtil.add_job_status(self.job_id, 15, 'Nf instancing apply grant finish')
        logger.info("Nf instancing apply grant finish")

    def apply_res(self, args):
        try:
            logger.info('apply_res, args=%s' % args)
            # ApplyResTask(args).do_biz()
            return {'result': '100', 'msg': 'Nf instancing apply resource finish', 'context': {}}
        except Exception as e:
            logger.error('Nf instancing apply resource exception=%s' % e.message)
            logger.error(traceback.format_exc())
            return {'result': '255', 'msg': 'Nf instancing apply resource exception', 'context': {}}

    def check_res_status(self, args):
        try:
            logger.info('check_res_status, args=%s' % args)
            # CheckResStatusTask(args).do_biz()
            return {'result': '100', 'msg': 'Nf instancing check resource status finish', 'context': {}}
        except Exception as e:
            logger.error('Nf instancing check resource status exception=%s' % e.message)
            logger.error(traceback.format_exc())
            return {'result': '255', 'msg': 'Nf instancing check resource status exception', 'context': {}}

    def wait_inst_finish(self, args):
        try:
            logger.info('wait_inst_finish, args=%s' % args)
            # WaitInstFinishTask(args).do_biz()
            return {'result': '100', 'msg': 'Nf instancing wait finish', 'context': {}}
        except Exception as e:
            logger.error('Nf instancing wait exception=%s' % e.message)
            logger.error(traceback.format_exc())
            return {'result': '255', 'msg': 'Nf instancing wait exception', 'context': {}}

    def lcm_notify(self, args):
        try:
            logger.info('lcm_notify, args=%s' % args)
            # LcmNotifyTask(args).do_biz()
            return {'result': '100', 'msg': 'Nf instancing lcm notify finish', 'context': {}}
        except Exception as e:
            logger.error('Nf instancing lcm notify exception=%s' % e.message)
            logger.error(traceback.format_exc())
            return {'result': '255', 'msg': 'Nf instancing lcm notify exception', 'context': {}}

    def inst_exception(self, args):
        try:
            logger.info('inst_exception, args=%s' % args)
            # InstExceptionTask(args).do_biz()
            return {'result': '100', 'msg': 'Nf instancing exception process finish', 'context': {}}
        except Exception as e:
            logger.error('Nf instancing exception process exception=%s' % e.message)
            logger.error(traceback.format_exc())
            return {'result': '255', 'msg': 'Nf instancing exception process exception', 'context': {}}

    def load_nfvo_config(self):
        logger.info("[NF instantiation]get nfvo connection info start")
        reg_info = NfvoRegInfoModel.objects.filter(vnfminstid='vnfm111').first()
        if reg_info:
            self.nfvo_inst_id = reg_info.nfvoid
            logger.info("[NF instantiation] Registered nfvo id is [%s]"%self.nfvo_inst_id)
        else:
            JobUtil.add_job_status(self.job_id, 255, "Nfvo was not registered")
            raise NFLCMException("Nfvo was not registered")
        logger.info("[NF instantiation]get nfvo connection info end")
