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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.nf.biz.create_vnf import CreateVnf
from lcm.nf.biz.query_vnf import QueryVnf
from lcm.nf.biz.update_vnf import UpdateVnf
from lcm.nf.biz.delete_vnf import DeleteVnf
from lcm.nf.serializers.create_vnf_req import CreateVnfReqSerializer
from lcm.nf.serializers.vnf_instance import VnfInstanceSerializer
from lcm.nf.serializers.vnf_instances import VnfInstancesSerializer
from lcm.nf.serializers.vnf_info_modifications import VnfInfoModificationsSerializer
from lcm.pub.exceptions import NFLCMException
from lcm.nf.const import VNF_STATUS
from lcm.nf.const import OPERATION_TYPE
from .common import view_safe_call_with_log
from .common import deal_vnf_action
from .common import deal_indivdual_query
from lcm.pub.exceptions import NFLCMExceptionBadRequest

logger = logging.getLogger(__name__)


class CreateVnfAndQueryVnfs(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: VnfInstancesSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def get(self, request):
        logger.debug("QueryMultiVnf--get::> %s" % request.data)
        resp_data = QueryVnf(request.data).query_multi_vnf()
        if len(resp_data) == 0:
            return Response(data=[], status=status.HTTP_200_OK)
        vnf_instances_serializer = VnfInstancesSerializer(data=resp_data)
        if not vnf_instances_serializer.is_valid():
            raise NFLCMException(vnf_instances_serializer.errors)

        return Response(data=resp_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=CreateVnfReqSerializer(),
        responses={
            status.HTTP_201_CREATED: VnfInstanceSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def post(self, request):
        logger.debug("CreateVnfIdentifier--post::> %s" % request.data)
        req_serializer = CreateVnfReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            raise NFLCMExceptionBadRequest(req_serializer.errors)

        nf_inst = CreateVnf(request.data).do_biz()
        rsp_data = {"id": nf_inst.nfinstid,
                    "vnfProvider": nf_inst.vendor,
                    "vnfdVersion": nf_inst.version,
                    "vnfPkgId": nf_inst.package_id,
                    "instantiationState": nf_inst.status}
        create_vnf_resp_serializer = VnfInstanceSerializer(data=rsp_data)
        if not create_vnf_resp_serializer.is_valid():
            raise NFLCMException(create_vnf_resp_serializer.errors)

        return Response(data=rsp_data, status=status.HTTP_201_CREATED)


class DeleteVnfAndQueryVnf(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: VnfInstanceSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def get(self, request, instanceid):
        logger.debug("QuerySingleVnf--get::> %s" % request.data)

        return deal_indivdual_query(res_serializer=VnfInstanceSerializer,
                                    query_fun=QueryVnf(
                                        request.data,
                                        instanceid).query_single_vnf)

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: "Successfully",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def delete(self, request, instanceid):
        logger.debug("DeleteVnfIdentifier--delete::> %s" % instanceid)

        DeleteVnf(request.data, instanceid).do_biz()

        return Response(data=None, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=VnfInfoModificationsSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: "Successfully",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def patch(self, request, instanceid):
        return deal_vnf_action(
            logger=logger,
            opt_type=OPERATION_TYPE.MODIFY_INFO,
            opt_status=VNF_STATUS.UPDATING,
            instid=instanceid,
            req=request,
            req_serializer=VnfInfoModificationsSerializer,
            act_task=UpdateVnf
        )
