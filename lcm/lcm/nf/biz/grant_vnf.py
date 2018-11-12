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
from lcm.nf.const import GRANT_TYPE

logger = logging.getLogger(__name__)


def grant_resource(data, nf_inst_id, job_id, grant_type, vdus):
    logger.info("Grant resource begin")

    content_args = {
        'vnfInstanceId': nf_inst_id,
        'vnfLcmOpOccId': job_id,
        # 'vnfdId': None,  # TODO
        # 'flavourId': "default",  # TODO
        'operation': grant_type,
        'isAutomaticInvocation': True,  # TODO
        # 'instantiationLevelId': None,  # TODO
        # 'addResources': [],
        # 'tmpResources': [],
        # 'updateResources': [],
        # 'removeResources': [],
        # 'placementConstraints': [],
        # 'vimConstraints': [],
        # 'additionalParams': {}
        # '_links': None  # TODO
    }

    if grant_type == GRANT_TYPE.TERMINATE:
        res_index = 1
        content_args['removeResources'] = []
        for vdu in vdus:
            res_def = {
                'id': str(res_index),
                'type': 'COMPUTE',
                'vduId': None,
                'resourceTemplateId': None,
                'resource': {
                    'vimConnectionId': None,
                    'resourceProviderId': None,
                    'resourceid': vdu.resourceid,
                    'vimLevelResourceType': None
                }
            }
            content_args['removeResources'].append(res_def)
            res_index += 1
        if vdus and vdus[0].vimid:
            content_args['additionalParams'] = {}
            content_args['additionalParams']['vimid'] = vdus[0].vimid
    elif grant_type == GRANT_TYPE.INSTANTIATE:
        vim_id = ignore_case_get(ignore_case_get(data, "additionalParams"), "vimId")
        res_index = 1
        content_args['addResources'] = []
        for vdu in vdus:
            res_def = {
                'id': str(res_index),
                'type': 'COMPUTE',
                # 'vduId': vdu["vdu_id"],
                'resourceTemplateId': vdu["vdu_id"]  # , None,
                # 'resource': None
            }
            content_args['addResources'].append(res_def)
            res_index += 1
        if vim_id:
            content_args['additionalParams'] = {}
            content_args['additionalParams']['vimid'] = vim_id
    elif grant_type == GRANT_TYPE.OPERATE:
        res_index = 1
        content_args['updateResources'] = []
        for vdu in vdus:
            res_def = {
                'id': str(res_index),
                'type': 'COMPUTE',
                'vduId': None,
                'resourceTemplateId': None,
                'resource': {
                    'vimConnectionId': None,
                    'resourceProviderId': None,
                    'resourceid': vdu.resourceid,
                    'vimLevelResourceType': None
                }
            }
            content_args['updateResources'].append(res_def)
            res_index += 1
        if vdus[0].vimid:
            content_args['additionalParams'] = {}
            content_args['additionalParams']['vimid'] = vdus[0].vimid

    vnfInsts = NfInstModel.objects.filter(nfinstid=nf_inst_id)
    if vnfInsts[0].vnfminstid:
        content_args['additionalParams'] = {}
        content_args['additionalParams']['vnfmid'] = vnfInsts[0].vnfminstid
    logger.info('Grant request data=%s' % content_args)
    apply_result = apply_grant_to_nfvo(json.dumps(content_args))
    logger.info("apply_result: %s" % apply_result)
    return apply_result
