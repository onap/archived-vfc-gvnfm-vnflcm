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

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.nf.vnfs.vnf_create.create_vnf_identifier import CreateVnf
from lcm.nf.vnfs.vnf_create.inst_vnf import InstVnf
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class CreateVnfIdentifier(APIView):
    def post(self, request):
        logger.debug("CreateVnfIdentifier--post::> %s" % request.data)
        data = {}
        data["vnfdId"] = ignore_case_get(request.data, "vnfdId")
        data["vnfInstanceName"] = ignore_case_get(request.data, "vnfInstanceName")
        data["vnfInstanceDescription"] = ignore_case_get(request.data, "vnfInstanceDescription")
        try:
            self.nf_inst_id = CreateVnf(data).do_biz()
        except Exception as e:
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        rsp = {"vnfInstanceId": self.nf_inst_id}
        return Response(data=rsp, status=status.HTTP_201_CREATED)


class InstantiateVnf(APIView):
    def post(self, request, instanceId):
        logger.debug("InstantiateVnf--post::> %s" % request.data)
        data = {'flavourId': ignore_case_get(request.data, 'flavourId'),
                'instantiationLevelId': ignore_case_get(request.data, 'instantiationLevelId'),
                'extVirtualLinks': ignore_case_get(request.data, 'extVirtualLinks'),
                'localizationLanguage': ignore_case_get(request.data, 'localizationLanguage'),
                'additionalParams': ignore_case_get(request.data, 'additionalParams')}
        nf_inst_id = instanceId
        job_id = JobUtil.create_job('NF', 'INSTANTIATE', nf_inst_id)
        JobUtil.add_job_status(job_id, 0, "INST_VNF_READY")

        InstVnf(data, nf_inst_id, job_id).start()
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