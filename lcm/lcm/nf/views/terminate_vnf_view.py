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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from lcm.nf.biz.terminate_vnf import TerminateVnf
from lcm.nf.serializers.terminate_vnf_req import TerminateVnfRequestSerializer
from lcm.nf.serializers.job_identifier import JobIdentifierSerializer
from lcm.nf.const import VNF_STATUS
from lcm.nf.const import OPERATION_TYPE
from .common import view_safe_call_with_log
from .common import deal_vnf_action

logger = logging.getLogger(__name__)


class TerminateVnfView(APIView):
    @swagger_auto_schema(
        request_body=TerminateVnfRequestSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: JobIdentifierSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def post(self, request, instanceid):
        return deal_vnf_action(
            logger=logger,
            opt_type=OPERATION_TYPE.TERMINATE,
            opt_status=VNF_STATUS.TERMINATING,
            instid=instanceid,
            req=request,
            req_serializer=TerminateVnfRequestSerializer,
            act_task=TerminateVnf
        )
