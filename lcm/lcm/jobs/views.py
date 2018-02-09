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

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.jobs.job_get import GetJobInfoService
from lcm.jobs.serializers import JobQueryRespSerializer
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class JobView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('responseId',
                              openapi.IN_QUERY,
                              "responseId",
                              type=openapi.TYPE_INTEGER
                              ),
        ],
        responses={
            status.HTTP_200_OK: JobQueryRespSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def get(self, request, job_id):
        try:
            response_id = ignore_case_get(request.META, 'responseId')
            ret = GetJobInfoService(job_id, response_id).do_biz()
            resp_serializer = JobQueryRespSerializer(data=ret)
            if not resp_serializer.is_valid():
                raise NFLCMException(resp_serializer.errors)
            return Response(data=resp_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(data={'error': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
