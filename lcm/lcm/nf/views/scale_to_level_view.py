# Copyright (C) 2019 ZTE. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
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

from lcm.nf.serializers.scale_vnf_to_level_request_serializer import ScaleVnfToLevelRequestSerializer
from lcm.nf.serializers.response import ProblemDetailsSerializer
from lcm.nf.biz.scale_vnf_to_level import ScaleVnfToLevel
from lcm.nf.const import VNF_STATUS
from lcm.nf.const import OPERATION_TYPE
from .common import view_safe_call_with_log
from .common import deal_vnf_action

logger = logging.getLogger(__name__)


class ScaleVnfToLevelView(APIView):
    @swagger_auto_schema(
        request_body=ScaleVnfToLevelRequestSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: "Success",
            status.HTTP_404_NOT_FOUND: ProblemDetailsSerializer(),
            status.HTTP_409_CONFLICT: ProblemDetailsSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def post(self, request, instanceid):
        return deal_vnf_action(
            logger=logger,
            opt_type=OPERATION_TYPE.SCALE_TO_LEVEL,
            opt_status=VNF_STATUS.SCALING,
            instid=instanceid,
            req=request,
            req_serializer=ScaleVnfToLevelRequestSerializer,
            act_task=ScaleVnfToLevel
        )
