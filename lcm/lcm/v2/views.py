# Copyright 2018 ZTE Corporation.
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

from lcm.nf.serializers import CreateVnfReqSerializer, CreateVnfRespSerializer
from lcm.nf.vnf_create.create_vnf_identifier import CreateVnf
from lcm.pub.exceptions import NFLCMException
from lcm.v2.serializers import VnfInstanceSerializer

logger = logging.getLogger(__name__)


class CreateVnfAndQueryVnfs(APIView):
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
