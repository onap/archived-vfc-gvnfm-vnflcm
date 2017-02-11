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
import json
import logging
import os
import traceback

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.nf.vnfs.vnf_create.create_vnf_identifier import CreateVnf
from lcm.nf.vnfs.vnf_create.inst_vnf import InstVnf
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.jobutil import JobUtil

logger = logging.getLogger(__name__)


class CreateVnfIdentifier(APIView):
    def post(self, request):
        logger.debug("CreateVnfIdentifier--post::> %s" % request.data)
        try:
            nf_inst_id = CreateVnf(request.data).do_biz()
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            logger.error(traceback.format_exc())
            return Response(data='unexpected exception', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        rsp = {"vnfInstanceId": nf_inst_id}
        return Response(data=rsp, status=status.HTTP_201_CREATED)


class InstantiateVnf(APIView):
    def post(self, request, instanceId):
        logger.debug("InstantiateVnf--post::> %s" % request.data)
        job_id = JobUtil.create_job('NF', 'INSTANTIATE', instanceId)
        JobUtil.add_job_status(job_id, 0, "INST_VNF_READY")
        InstVnf(request.data, instanceId, job_id).start()
        rsp = {"jobId": job_id}
        return Response(data=rsp, status=status.HTTP_202_ACCEPTED)


class DeleteVnfIdentifier(APIView):
    def delete(self, request):
        logger.debug("DeleteVnfIdentifier--delete::> %s" % request.data)
        return Response(data='', status=status.HTTP_202_ACCEPTED)


class TerminateVnf(APIView):
    def post(self, request):
        logger.debug("TerminateVnf--post::> %s" % request.data)
        return Response(data='', status=status.HTTP_202_ACCEPTED)


class QueryMultipleVnf(APIView):
    def get(self, request):
        logger.debug("QueryMultipleVnf--get::> %s" % request.data)
        return Response(data='', status=status.HTTP_202_ACCEPTED)


class QuerySingleVnf(APIView):
    def get(self, request):
        logger.debug("QuerySingleVnf--get::> %s" % request.data)
        return Response(data='', status=status.HTTP_202_ACCEPTED)


class GetOperationStatus(APIView):
    def get(self, request):
        logger.debug("GetOperationStatus--get::> %s" % request.data)
        return Response(data='', status=status.HTTP_202_ACCEPTED)


class SwaggerJsonView(APIView):
    def get(self, request):
        json_file = os.path.join(os.path.dirname(__file__), 'swagger.json')
        f = open(json_file)
        json_data = json.JSONDecoder().decode(f.read())
        f.close()
        return Response(json_data)
