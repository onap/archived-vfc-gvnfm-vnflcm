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

import logging
import traceback

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.nf.biz.query_vnf_lcm_op_occ import QueryVnfLcmOpOcc
from lcm.nf.serializers.error_types import ProblemDetailsSerializer
from lcm.nf.serializers.vnf_lcm_op_occs import VNFLCMOpOccsSerializer
from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)
EXCLUDE_DEFAULT = ['operationParams', 'error', 'resourceChanges', 'changedInfo', 'changedExtConnectivity']
VALID_FILTERS = ["all_fields", "fields", "exclude_fields", "exclude_default",
                 "id", "operationState", "stateEnteredTime", "startTime",
                 "vnfInstanceId", "grantId", "operation"]


def get_problem_details_serializer(status_code, error_message):
    problem_details = {
        "status": status_code,
        "detail": error_message
    }
    problem_details_serializer = ProblemDetailsSerializer(data=problem_details)
    problem_details_serializer.is_valid()
    return problem_details_serializer


class QueryMultiVnfLcmOpOccs(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: VNFLCMOpOccsSerializer(),
            status.HTTP_400_BAD_REQUEST: ProblemDetailsSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: ProblemDetailsSerializer()
        }
    )
    def get(self, request):
        logger.debug("QueryMultiVnfLcmOpOccs--get::> %s" % request.query_params)
        try:
            if request.query_params and not set(request.query_params).issubset(set(VALID_FILTERS)):
                problem_details_serializer = get_problem_details_serializer(400, "Not a valid filter")
                return Response(data=problem_details_serializer.data, status=status.HTTP_400_BAD_REQUEST)
            resp_data = QueryVnfLcmOpOcc(request.query_params).query_multi_vnf_lcm_op_occ()

            vnf_lcm_op_occs_serializer = VNFLCMOpOccsSerializer(data=resp_data)
            if not vnf_lcm_op_occs_serializer.is_valid():
                raise NFLCMException(vnf_lcm_op_occs_serializer.errors)

            logger.debug("QueryMultiVnfLcmOpOccs--get::> Remove default fields if exclude_default" +
                         " is specified")
            # TODO(bharath): Add support for "fields", "exclude_fields" in query parameters
            if 'exclude_default' in request.query_params.keys():
                for field in EXCLUDE_DEFAULT:
                    for lcm_op in vnf_lcm_op_occs_serializer.data:
                        del lcm_op[field]
            return Response(data=vnf_lcm_op_occs_serializer.data, status=status.HTTP_200_OK)
        except NFLCMException as e:
            logger.error(e.message)
            problem_details_serializer = get_problem_details_serializer(500, e.message)
            return Response(data=problem_details_serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            problem_details_serializer = get_problem_details_serializer(500, e.message)
            return Response(data=problem_details_serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
