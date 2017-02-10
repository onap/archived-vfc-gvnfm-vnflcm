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
from lcm.pub.msapi.nfvolcm import vnfd_rawdata_get
from lcm.pub.utils.jobutil import JobUtil

logger = logging.getLogger(__name__)


class InstVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(InstVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id

    def run(self):
        try:
            self.inst_pre(self.nf_inst_id)

            # self.apply_grant(args)
            # self.apply_res(args)
            # self.check_res_status(args)
            # self.wait_inst_finish(args)
            # self.lcm_notify(args)
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
        if vnf_inst.instantiationState != 'NOT_INSTANTIATED':
            logger.error("VNF instantiationState is not NOT_INSTANTIATED.")
            JobUtil.add_job_status(self.job_id, 255, "VNF instantiationState is not NOT_INSTANTIATED.")
            raise NFLCMException('VNF instantiationState is not NOT_INSTANTIATED.')

        #get rawdata by vnfd_id
        ret = vnfd_rawdata_get(vnf_inst.vnfdid)
        if ret[0] != 0:
            raise NFLCMException("Get vnfd_raw_data failed.")
        dst_plan = json.JSONDecoder().decode(ret[1])
        #checkParameterExist
        for cp in self.data:
            if cp not in dst_plan:
                logger.error("[%s] is not defined in vnfd_info."%cp)
                JobUtil.add_job_status(self.job_id, 255, "Input parameter is not defined in vnfd_info.")
                raise NFLCMException('Input parameter is not defined in vnfd_info.')

        JobUtil.add_job_status(self.job_id, 2, 'GET_NFVO_CONNECTION_INFO')
        self.load_global_config()

        JobUtil.add_job_status(self.job_id, 100, "Instantiate Vnf success.")
        is_exist = JobStatusModel.objects.filter(jobid=self.job_id).exists()
        logger.debug("check_ns_inst_name_exist::is_exist=%s" % is_exist)

    def apply_grant(self, args):
        try:
            logger.info('apply_grant, args=%s' % args)
            # ApplyGrantTask(args).do_biz()
            return {'result': '100', 'msg': 'Nf instancing apply grant finish', 'context': {}}
        except Exception as e:
            logger.error('Nf instancing apply grant exception=%s' % e.message)
            logger.error(traceback.format_exc())
            return {'result': '255', 'msg': 'Nf instancing apply grant exception', 'context': {}}

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

    def load_global_config(self):
        logger.info("[NF instantiation]get nfvo connection info start")
        reg_info = NfvoRegInfoModel.objects.filter(vnfminstid='vnfm111').first()
        if reg_info:
            self.nfvo_reg_info = reg_info.nfvoid
            logger.info("[NF instantiation] Registered nfvo id is [%s]"%self.nfvo_reg_info)
        else:
            JobUtil.add_job_status(self.job_id, 255, "Nfvo was not registered")
            raise NFLCMException("Nfvo was not registered")
        logger.info("[NF instantiation]get nfvo connection info end")