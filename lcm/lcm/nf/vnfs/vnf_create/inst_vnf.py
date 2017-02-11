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
from lcm.pub.msapi.nfvolcm import vnfd_rawdata_get, apply_grant_to_nfvo, apply_res_to_nfvo
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get

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
            self.inst_pre()
            self.apply_grant()
            self.create_res()
            # self.check_res_status(args)
            # self.wait_inst_finish(args)
            # self.lcm_notify(args)
            JobUtil.add_job_status(self.job_id, 100, "Instantiate Vnf success.")
            is_exist = JobStatusModel.objects.filter(jobid=self.job_id).exists()
            logger.debug("check_ns_inst_name_exist::is_exist=%s" % is_exist)
        except NFLCMException as e:
            self.vnf_inst_failed_handle(e.message)
            # self.rollback(e.message)
        except:
            self.vnf_inst_failed_handle('unexpected exception')
            logger.error(traceback.format_exc())
            # self.rollback('unexpected exception')

    def inst_pre(self):
        vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if not vnf_insts.exists():
            raise NFLCMException('VNF nf_inst_id is not exist.')

        self.vnfm_inst_id = vnf_insts[0].vnfm_inst_id
        if vnf_insts[0].instantiationState != 'NOT_INSTANTIATED':
            raise NFLCMException('VNF instantiationState is not NOT_INSTANTIATED.')

        #get rawdata by vnfd_id
        ret = vnfd_rawdata_get(vnf_insts[0].vnfdid)
        if ret[0] != 0:
            raise NFLCMException("Get vnfd_raw_data failed.")
        self.vnfd_info = json.JSONDecoder().decode(ret[1])
        #checkParameterExist
        for cp in self.data:
            if cp not in self.vnfd_info:
                raise NFLCMException('Input parameter is not defined in vnfd_info.')
        #get nfvo info
        JobUtil.add_job_status(self.job_id, 5, 'GET_NFVO_CONNECTION_INFO')
        self.load_nfvo_config()

        #update NfInstModel
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(flavour_id=ignore_case_get(self.data, "flavourId"),
                                                                    vnf_level=ignore_case_get(self.data, 'instantiationLevelId'),
                                                                    input_params=ignore_case_get(self.data, 'additionalParams'),
                                                                    extension=ignore_case_get(self.data, ''),
                                                                    initallocatedata=self.vnfd_info,
                                                                    localizationLanguage=ignore_case_get(self.data, 'localizationLanguage'),
                                                                    lastuptime=now_time())

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
            raise NFLCMException('Nf instancing apply grant exception')

        #update_resources_table()
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(instantiationState='INSTANTIATED', lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 15, 'Nf instancing apply grant finish')
        logger.info("Nf instancing apply grant finish")

    def create_res(self):
        logger.info("[NF instantiation] send resource apply request start")
        content_args = {'nfvoInstanceId': self.nfvo_inst_id, 'vnfmInstanceId': self.vnfm_inst_id,
                        'nfInstanceId': self.nf_inst_id, 'nfDescriptorId': '',
                        'lifecycleOperation': 'Instantiate', 'jobId': '',
                        'allocateData': self.vnfd_info}
        volumns = ignore_case_get(self.data, "volumn_storages")
        #call vim driver api
        #create_volumns(volumns)
        JobUtil.add_job_status(self.job_id, 35, 'Nf instancing create resource(volumn_storages) finish')
        # create_networks(self.vnfd_info)
        JobUtil.add_job_status(self.job_id, 45, 'Nf instancing create resource(networks) finish')
        # create_vdus(self.vnfd_info)
        JobUtil.add_job_status(self.job_id, 65, 'Nf instancing create resource(vms) finish')

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

    def rollback(self, args):
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
            raise NFLCMException("Nfvo was not registered")
        logger.info("[NF instantiation]get nfvo connection info end")

    def vnf_inst_failed_handle(self, error_msg):
        logger.error('VNF instantiation failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='failed', lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, error_msg)
        # JobUtil.add_job_status(self.job_id, 255, 'VNF instantiation failed, detail message: %s' % error_msg, 0)


