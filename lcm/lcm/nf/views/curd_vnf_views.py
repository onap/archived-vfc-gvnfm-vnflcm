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
from lcm.nf.biz.update_vnf import UpdateVnf
from lcm.nf.serializers.create_vnf_req import CreateVnfReqSerializer
from lcm.nf.serializers.vnf_instance import VnfInstanceSerializer
from lcm.nf.serializers.vnf_instances import VnfInstancesSerializer
from lcm.nf.serializers.vnf_info_modifications import VnfInfoModificationsSerializer
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.exceptions import NFLCMException
from lcm.pub.exceptions import NFLCMExceptionNotFound
from lcm.pub.database.models import NfInstModel
from lcm.nf.const import VNF_STATUS

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
            if len(resp_data) == 0:
                return Response(data=[], status=status.HTTP_200_OK)
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

            nf_inst = CreateVnf(request.data).do_biz()
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
        except NFLCMExceptionNotFound as e:
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(e.message)
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

    @swagger_auto_schema(
        request_body=VnfInfoModificationsSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: "Successfully",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def patch(self, request, instanceid):
        logger.debug("UpdateSingleVnf--patch::> %s, %s", instanceid, request.data)
        try:
            upd_vnf_serializer = VnfInfoModificationsSerializer(data=request.data)
            if not upd_vnf_serializer.is_valid():
                raise NFLCMException(upd_vnf_serializer.errors)

            job_id = JobUtil.create_job('NF', 'UPDATE', instanceid)
            JobUtil.add_job_status(job_id, 0, "UPDATE_VNF_READY")

            vnf_insts = NfInstModel.objects.filter(nfinstid=instanceid)
            if not vnf_insts.exists():
                raise NFLCMExceptionNotFound("VNF(%s) does not exist." % instanceid)
            vnf_insts.update(status=VNF_STATUS.UPDATING)

            JobUtil.add_job_status(job_id, 15, 'Nf updating pre-check finish')
            UpdateVnf(request.data, instanceid, job_id).start()

            return Response(data=None, status=status.HTTP_202_ACCEPTED)
        except NFLCMException as e:
            logger.error(e.message)
            logger.error('Update VNF instance[%s] failed' % instanceid)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except NFLCMExceptionNotFound as e:
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            logger.error('Update VNF instance[%s] failed' % instanceid)
            return Response(data={'error': 'unexpected exception'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
