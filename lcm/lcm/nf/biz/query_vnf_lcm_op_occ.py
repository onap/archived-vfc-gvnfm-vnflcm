# Copyright (C) 2018 Verizon. All Rights Reserved
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

from lcm.pub.database.models import VNFLcmOpOccModel
from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)
FILTERS = {
    'id': 'id',
    'operationState': 'operation_state',
    'stateEnteredTime': 'state_entered_time',
    'startTime': 'start_time',
    'vnfInstanceId': 'vnf_instance_id',
    'grantId': 'grant_id',
    'operation': 'operation'
}


class QueryVnfLcmOpOcc:
    def __init__(self, data, lcm_op_occ_id=''):
        self.vnf_lcm_op_occ_id = lcm_op_occ_id
        self.params = data

    def query_multi_vnf_lcm_op_occ(self):
        query_data = {}
        logger.debug("QueryMultiVnfLcmOpOccs--get--biz::> Check for filters in query params" % self.params)
        for query, value in self.params.iteritems():
            if query in FILTERS:
                query_data[FILTERS[query]] = value
        # Query the database with filters if the request has fields in request params, else fetch all records
        if query_data:
            lcm_ops = VNFLcmOpOccModel.objects.filter(**query_data)
        else:
            lcm_ops = VNFLcmOpOccModel.objects.all()
        if not lcm_ops.exists():
            raise NFLCMException('LCM Operation Occurances do not exist')
        return [self.fill_resp_data(lcm_op) for lcm_op in lcm_ops]

    def fill_resp_data(self, lcm_op):
        resp_data = {
            'id': lcm_op.id,
            'operationState': lcm_op.operation_state,
            'stateEnteredTime': lcm_op.state_entered_time,
            'startTime': lcm_op.start_time,
            'vnfInstanceId': lcm_op.vnf_instance_id,
            'grantId': None,
            'operation': lcm_op.operation,
            'isAutomaticInvocation': lcm_op.is_automatic_invocation,
            'operationParams': json.loads(lcm_op.operation_params),
            'isCancelPending': lcm_op.is_cancel_pending,
            'cancelMode': lcm_op.cancel_mode,
            'error': None if not lcm_op.error else json.loads(lcm_op.error),
            'resourceChanges': None if not lcm_op.resource_changes else json.loads(lcm_op.resource_changes),
            'changedInfo': None if not lcm_op.changed_info else json.loads(lcm_op.changed_info),
            'changedExtConnectivity': None if not lcm_op.changed_ext_connectivity else json.loads(lcm_op.changed_ext_connectivity),
            '_links': json.loads(lcm_op.links)
        }
        return resp_data

    def query_single_vnf_lcm_op_occ(self):
        lcm_op = VNFLcmOpOccModel.objects.filter(id=self.vnf_lcm_op_occ_id)
        if not lcm_op.exists():
            raise NFLCMException('LCM Operation Occurance does not exist')
        resp_data = self.fill_resp_data(lcm_op[0])
        return resp_data
