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

from lcm.nf.vnfs.serializers import CreateVnfReqSerializer, CreateVnfRespSerializer, VnfsInfoSerializer, \
    InstantiateVnfResponseSerializer, InstantiateVnfRequestSerializer
from lcm.nf.vnfs.vnf_cancel.delete_vnf_identifier import DeleteVnf
from lcm.nf.vnfs.vnf_cancel.term_vnf import TermVnf
from lcm.nf.vnfs.vnf_create.create_vnf_identifier import CreateVnf
from lcm.nf.vnfs.vnf_create.inst_vnf import InstVnf
from lcm.nf.vnfs.vnf_query.query_vnf import QueryVnf
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.jobutil import JobUtil

logger = logging.getLogger(__name__)


class CreateVnfAndQueryVnfs(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: VnfsInfoSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def get(self, request):
        logger.debug("QueryMultiVnf--get::> %s" % request.data)
        try:
            resp_data = QueryVnf(request.data).query_multi_vnf()

            vnfsInfoSerializer = VnfsInfoSerializer(data=resp_data)
            resp_isValid = vnfsInfoSerializer.is_valid()
            if not resp_isValid:
                raise NFLCMException(vnfsInfoSerializer.errors)

            return Response(data=vnfsInfoSerializer.data, status=status.HTTP_200_OK)
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': 'Failed to get Vnfs'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=CreateVnfReqSerializer(),
        responses={
            status.HTTP_201_CREATED: CreateVnfRespSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def post(self, request):
        logger.debug("CreateVnfIdentifier--post::> %s" % request.data)
        req_serializer = CreateVnfReqSerializer(data=request.data)
        req_isValid = req_serializer.is_valid()
        try:
            if not req_isValid:
                raise NFLCMException(req_serializer.errors)

            nf_inst_id = CreateVnf(req_serializer.data).do_biz()

            resp_serializer = CreateVnfRespSerializer(data={"vnfInstanceId": nf_inst_id})
            resp_isValid = resp_serializer.is_valid()
            if not resp_isValid:
                raise NFLCMException(resp_serializer.errors)
            return Response(data=resp_serializer.data, status=status.HTTP_201_CREATED)
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': 'unexpected exception'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InstantiateVnf(APIView):
    @swagger_auto_schema(
        request_body=InstantiateVnfRequestSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: InstantiateVnfResponseSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def post(self, request, instanceid):
        logger.debug("InstantiateVnf--post::> %s" % request.data)
        instantiateVnfRequestSerializer = InstantiateVnfRequestSerializer(data=request.data)
        req_isValid = instantiateVnfRequestSerializer.is_valid()
        try:
            if not req_isValid:
                raise NFLCMException(instantiateVnfRequestSerializer.errors)

            job_id = JobUtil.create_job('NF', 'INSTANTIATE', instanceid)
            JobUtil.add_job_status(job_id, 0, "INST_VNF_READY")
            InstVnf(instantiateVnfRequestSerializer.data, instanceid, job_id).start()

            instantiateVnfResponseSerializer = InstantiateVnfResponseSerializer(data={"jobId": job_id})
            resp_isValid = instantiateVnfResponseSerializer.is_valid()
            if not resp_isValid:
                raise NFLCMException(instantiateVnfResponseSerializer.errors)

            return Response(data=instantiateVnfResponseSerializer.data, status=status.HTTP_202_ACCEPTED)
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': 'unexpected exception'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteVnfAndQueryVnf(APIView):
    def get(self, request, instanceid):
        logger.debug("QuerySingleVnf--get::> %s" % request.data)
        try:
            resp_data = QueryVnf(request.data, instanceid).query_single_vnf()
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.eror(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': 'Failed to get Vnf(%s)' % instanceid},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data=resp_data, status=status.HTTP_200_OK)

    def delete(self, request, instanceid):
        logger.debug("DeleteVnfIdentifier--delete::> %s" % request.data)
        try:
            DeleteVnf(request.data, instanceid).do_biz()
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': 'unexpected exception'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data=None, status=status.HTTP_204_NO_CONTENT)


class TerminateVnf(APIView):
    def post(self, request, instanceid):
        logger.debug("TerminateVnf--post::> %s" % request.data)
        try:
            job_id = JobUtil.create_job('NF', 'TERMINATE', instanceid)
            JobUtil.add_job_status(job_id, 0, "TERM_VNF_READY")
            TermVnf(request.data, instanceid, job_id).start()
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': 'unexpected exception'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        rsp = {
            "jobId": job_id
        }
        return Response(data=rsp, status=status.HTTP_202_ACCEPTED)
