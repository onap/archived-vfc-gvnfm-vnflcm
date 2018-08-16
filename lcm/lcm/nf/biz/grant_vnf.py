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

from lcm.pub.database.models import NfInstModel
from lcm.pub.msapi.gvnfmdriver import apply_grant_to_nfvo
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


def grant_resource(data, nf_inst_id, job_id, grant_type, vdus):
    logger.info("Grant resource begin")
    if grant_type == "Terminate":
        lifecycleOperration = "Terminate"
    elif grant_type == "Instantiate":
        lifecycleOperration = "Instantiate"

    content_args = {
        'vnfInstanceId': nf_inst_id,
        'vnfDescriptorId': '',
        'lifecycleOperation': lifecycleOperration,
        'vnfLcmOpOccId': job_id,
        'addResources': [],
        'removeResources': [],
        'placementConstraints': [],
        'additionalParams': {}
    }

    if grant_type == "Terminate":
        res_index = 1
        for vdu in vdus:
            res_def = {
                'type': 'VDU',
                'resDefId': str(res_index),
                'resDesId': vdu.resouceid}
            content_args['removeResources'].append(res_def)
            res_index += 1
        content_args['additionalParams']['vimid'] = vdus[0].vimid
    elif grant_type == "Instantiate":
        vim_id = ignore_case_get(ignore_case_get(data, "additionalParams"), "vimId")
        res_index = 1
        for vdu in vdus:
            res_def = {
                'type': 'VDU',
                'resDefId': str(res_index),
                'resDesId': ignore_case_get(vdu, "vdu_id")
            }
            content_args['addResources'].append(res_def)
            res_index += 1
        content_args['additionalParams']['vimid'] = vim_id

    vnfInsts = NfInstModel.objects.filter(nfinstid=nf_inst_id)
    content_args['additionalParams']['vnfmid'] = vnfInsts[0].vnfminstid
    logger.info('Grant request data=%s' % content_args)
    apply_result = apply_grant_to_nfvo(json.dumps(content_args))
    return apply_result
