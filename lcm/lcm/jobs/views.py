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

from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.jobs.job_get import GetJobInfoService

logger = logging.getLogger(__name__)


class JobView(APIView):
    def get(self, request, job_id):
        response_id = request.GET.get('responseId')
        ret = GetJobInfoService(job_id, response_id).do_biz()
        return Response(data=ret)
