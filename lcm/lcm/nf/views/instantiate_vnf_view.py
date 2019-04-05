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
from lcm.nf.biz.instantiate_vnf import InstantiateVnf
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.nf.serializers.instantiate_vnf_request import InstantiateVnfRequestSerializer
from lcm.nf.serializers.job_identifier import JobIdentifierSerializer
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.jobutil import JobUtil

logger = logging.getLogger(__name__)


class InstantiateVnfView(APIView):
    @swagger_auto_schema(
        request_body=InstantiateVnfRequestSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: JobIdentifierSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def post(self, request, instanceid):
        logger.debug("InstantiateVnf--post::> %s" % request.data)

        instantiate_vnf_request_serializer = InstantiateVnfRequestSerializer(data=request.data)
        if not instantiate_vnf_request_serializer.is_valid():
            raise NFLCMException(instantiate_vnf_request_serializer.errors)

        job_id = JobUtil.create_job('NF', 'INSTANTIATE', instanceid)
        JobUtil.add_job_status(job_id, 0, "INST_VNF_READY")
        InstantiateVnf(instantiate_vnf_request_serializer.data, instanceid, job_id).start()

        job_identifier_serializer = JobIdentifierSerializer(data={"jobId": job_id})
        resp_isvalid = job_identifier_serializer.is_valid()
        if not resp_isvalid:
            raise NFLCMException(job_identifier_serializer.errors)

        return Response(data=job_identifier_serializer.data, status=status.HTTP_202_ACCEPTED)
