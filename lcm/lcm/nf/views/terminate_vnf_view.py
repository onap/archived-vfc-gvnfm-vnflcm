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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.nf.biz.terminate_vnf import TerminateVnf
from lcm.nf.serializers.terminate_vnf_req import TerminateVnfRequestSerializer
from lcm.nf.serializers.job_identifier import JobIdentifierSerializer
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.database.models import NfInstModel

logger = logging.getLogger(__name__)


class TerminateVnfView(APIView):
    @swagger_auto_schema(
        request_body=TerminateVnfRequestSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: JobIdentifierSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def post(self, request, instanceid):
        logger.debug("TerminateVnf--post::> %s" % request.data)
        try:
            terminate_vnf_request_serializer = TerminateVnfRequestSerializer(data=request.data)
            if not terminate_vnf_request_serializer.is_valid():
                raise NFLCMException(terminate_vnf_request_serializer.errors)

            job_id = JobUtil.create_job('NF', 'TERMINATE', instanceid)
            JobUtil.add_job_status(job_id, 0, "TERM_VNF_READY")
            TerminateVnf(terminate_vnf_request_serializer.data, instanceid, job_id).start()

            terminate_vnf_response_serializer = JobIdentifierSerializer(data={"jobId": job_id})
            if not terminate_vnf_response_serializer.is_valid():
                raise NFLCMException(terminate_vnf_response_serializer.errors)

            return Response(data=terminate_vnf_response_serializer.data, status=status.HTTP_202_ACCEPTED)
        except NFLCMException as e:
            self.vnf_term_failed_handle(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            self.vnf_term_failed_handle(traceback.format_exc())
            return Response(data={'error': 'unexpected exception'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def vnf_term_failed_handle(self, error_msg):
        logger.error('VNF termination failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='failed', lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, error_msg)
