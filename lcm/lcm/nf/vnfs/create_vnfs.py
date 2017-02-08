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

from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)


class CreateVnfs(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(CreateVnfs, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id

    def run(self):
        try:
            args = {}
            self.inst_pre(args)
            self.apply_grant(args)
            self.apply_res(args)
            self.check_res_status(args)
            self.wait_inst_finish(args)
            self.lcm_notify(args)
        except NFLCMException as e:
            self.inst_exception(e.message)
            pass
        except Exception:
            logger.error(traceback.format_exc())
            self.inst_exception('unexpected exception')

    def inst_pre(self, args):
        try:
            logger.info('inst_pre, args=%s' % args)
            # InstPreTask(args).do_biz()
            return {'result': '100', 'sessionid': '', 'msg': 'Nf instancing preprocess finish', 'context': {}}
        except Exception as e:
            logger.error('Nf instancing preprocess exception=%s' % e.message)
            logger.error(traceback.format_exc())
            return {'result': '255', 'msg': 'Nf instancing preprocess exception', 'context': {}}

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