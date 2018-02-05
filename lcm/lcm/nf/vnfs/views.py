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
    InstOrTeriVnfResponseSerializer, InstantiateVnfRequestSerializer, VnfInfoSerializer, TerminateVnfRequestSerializer
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
        responses={
            status.HTTP_200_OK: VnfsInfoSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def get(self, request):
        logger.debug("QueryMultiVnf--get::> %s" % request.data)
        try:
            resp_data = QueryVnf(request.data).query_multi_vnf()

            vnfs_info_serializer = VnfsInfoSerializer(data=resp_data)
            if not vnfs_info_serializer.is_valid():
                raise NFLCMException(vnfs_info_serializer.errors)

            return Response(data=vnfs_info_serializer.data, status=status.HTTP_200_OK)
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
        try:
            req_serializer = CreateVnfReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise NFLCMException(req_serializer.errors)

            nf_inst_id = CreateVnf(req_serializer.data).do_biz()

            create_vnf_resp_serializer = CreateVnfRespSerializer(data={"vnfInstanceId": nf_inst_id})
            if not create_vnf_resp_serializer.is_valid():
                raise NFLCMException(create_vnf_resp_serializer.errors)
            return Response(data=create_vnf_resp_serializer.data, status=status.HTTP_201_CREATED)
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
            status.HTTP_202_ACCEPTED: InstOrTeriVnfResponseSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def post(self, request, instanceid):
        logger.debug("InstantiateVnf--post::> %s" % request.data)
        try:
            instantiate_vnf_request_serializer = InstantiateVnfRequestSerializer(data=request.data)
            if not instantiate_vnf_request_serializer.is_valid():
                raise NFLCMException(instantiate_vnf_request_serializer.errors)

            job_id = JobUtil.create_job('NF', 'INSTANTIATE', instanceid)
            JobUtil.add_job_status(job_id, 0, "INST_VNF_READY")
            InstVnf(instantiate_vnf_request_serializer.data, instanceid, job_id).start()

            instantiate_vnf_response_serializer = InstOrTeriVnfResponseSerializer(data={"jobId": job_id})
            resp_isvalid = instantiate_vnf_response_serializer.is_valid()
            if not resp_isvalid:
                raise NFLCMException(instantiate_vnf_response_serializer.errors)

            return Response(data=instantiate_vnf_response_serializer.data, status=status.HTTP_202_ACCEPTED)
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': 'unexpected exception'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteVnfAndQueryVnf(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: VnfInfoSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def get(self, request, instanceid):
        logger.debug("QuerySingleVnf--get::> %s" % request.data)
        try:
            resp_data = QueryVnf(request.data, instanceid).query_single_vnf()

            vnf_info_serializer = VnfInfoSerializer(data=resp_data)
            if not vnf_info_serializer.is_valid():
                raise NFLCMException(vnf_info_serializer.errors)

            return Response(data=vnf_info_serializer.data, status=status.HTTP_200_OK)
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.eror(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': 'Failed to get Vnf(%s)' % instanceid},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: "Successfully",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def delete(self, request, instanceid):
        logger.debug("DeleteVnfIdentifier--delete::> %s" % request.data)
        try:
            DeleteVnf(request.data, instanceid).do_biz()

            return Response(data=None, status=status.HTTP_204_NO_CONTENT)
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': 'unexpected exception'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TerminateVnf(APIView):
    @swagger_auto_schema(
        request_body=TerminateVnfRequestSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: InstOrTeriVnfResponseSerializer(),
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
            TermVnf(terminate_vnf_request_serializer.data, instanceid, job_id).start()

            terminate_vnf_response_serializer = InstOrTeriVnfResponseSerializer(data={"jobId": job_id})
            if not terminate_vnf_response_serializer.is_valid():
                raise NFLCMException(terminate_vnf_response_serializer.errors)

            return Response(data=terminate_vnf_response_serializer.data, status=status.HTTP_202_ACCEPTED)
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': 'unexpected exception'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
