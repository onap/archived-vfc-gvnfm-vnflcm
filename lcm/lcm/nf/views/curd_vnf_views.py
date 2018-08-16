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
from lcm.nf.biz.delete_vnf import DeleteVnf
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.nf.biz.create_vnf import CreateVnf
from lcm.nf.biz.query_vnf import QueryVnf
from lcm.nf.serializers.create_vnf_req import CreateVnfReqSerializer
from lcm.nf.serializers.vnf_instance import VnfInstanceSerializer
from lcm.nf.serializers.vnf_instances import VnfInstancesSerializer
from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)


class CreateVnfAndQueryVnfs(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: VnfInstancesSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def get(self, request):
        logger.debug("QueryMultiVnf--get::> %s" % request.data)
        try:
            resp_data = QueryVnf(request.data).query_multi_vnf()

            vnf_instances_serializer = VnfInstancesSerializer(data=resp_data)
            if not vnf_instances_serializer.is_valid():
                raise NFLCMException(vnf_instances_serializer.errors)

            return Response(data=vnf_instances_serializer.data, status=status.HTTP_200_OK)
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
            status.HTTP_201_CREATED: VnfInstanceSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def post(self, request):
        logger.debug("CreateVnfIdentifier--post::> %s" % request.data)
        try:
            req_serializer = CreateVnfReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise NFLCMException(req_serializer.errors)

            nf_inst = CreateVnf(req_serializer.data).do_biz()
            create_vnf_resp_serializer = VnfInstanceSerializer(data={"id": nf_inst.nfinstid,
                                                                     "vnfProvider": nf_inst.vendor,
                                                                     "vnfdVersion": nf_inst.version,
                                                                     "vnfPkgId": nf_inst.package_id,
                                                                     "instantiationState": nf_inst.status})
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


class DeleteVnfAndQueryVnf(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: VnfInstanceSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def get(self, request, instanceid):
        logger.debug("QuerySingleVnf--get::> %s" % request.data)
        try:
            resp_data = QueryVnf(request.data, instanceid).query_single_vnf()

            vnfs_instance_serializer = VnfInstanceSerializer(data=resp_data)
            if not vnfs_instance_serializer.is_valid():
                raise NFLCMException(vnfs_instance_serializer.errors)

            return Response(data=vnfs_instance_serializer.data, status=status.HTTP_200_OK)
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
            logger.debug('Delete VNF instance[%s] failed' % instanceid)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            logger.debug('Delete VNF instance[%s] failed' % instanceid)
            return Response(data={'error': 'unexpected exception'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
