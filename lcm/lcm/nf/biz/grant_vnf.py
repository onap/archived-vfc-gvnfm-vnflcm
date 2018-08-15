# Copyright 2018 ZTE Corporation.
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

from lcm.pub.database.models import NfInstModel, VmInstModel
from lcm.pub.msapi.gvnfmdriver import apply_grant_to_nfvo
from lcm.pub.utils.jobutil import JobUtil

logger = logging.getLogger(__name__)


def grant_resource(nf_inst_id, job_id):
    logger.info("Grant resource begin")
    content_args = {
        'vnfInstanceId': nf_inst_id,
        'vnfDescriptorId': '',
        'lifecycleOperation': 'Terminate',
        'vnfLcmOpOccId': job_id,
        'addResource': [],
        'removeResource': [],
        'placementConstraint': [],
        'additionalParam': {}
    }

    vdus = VmInstModel.objects.filter(instid=nf_inst_id, is_predefined=1)
    res_index = 1
    for vdu in vdus:
        res_def = {
            'type': 'VDU',
            'resDefId': str(res_index),
            'resDesId': vdu.resouceid}
        content_args['removeResource'].append(res_def)
        res_index += 1

    vnfInsts = NfInstModel.objects.filter(nfinstid=nf_inst_id)
    content_args['additionalParam']['vnfmid'] = vnfInsts[0].vnfminstid
    content_args['additionalParam']['vimid'] = vdus[0].vimid
    logger.info('Grant request data=%s' % content_args)
    apply_result = apply_grant_to_nfvo(json.dumps(content_args))
    logger.info("Grant resource end, response: %s" % apply_result)
