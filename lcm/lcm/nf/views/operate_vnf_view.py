# Copyright (C) 2018 Verizon. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
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

from lcm.nf.biz.operate_vnf import OperateVnf
from lcm.nf.serializers.operate_vnf_req import OperateVnfRequestSerializer
from lcm.nf.serializers.response import ProblemDetailsSerializer
from lcm.pub.exceptions import NFLCMException, NFLCMExceptionNotFound, NFLCMExceptionConflict
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.database.models import NfInstModel
from lcm.nf.const import VNF_STATUS

logger = logging.getLogger(__name__)


class OperateVnfView(APIView):
    @swagger_auto_schema(
        request_body=OperateVnfRequestSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: "Success",
            status.HTTP_404_NOT_FOUND: ProblemDetailsSerializer(),
            status.HTTP_409_CONFLICT: ProblemDetailsSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def post(self, request, instanceid):
        logger.debug("OperateVnf--post::> %s" % request.data)
        try:
            operate_vnf_request_serializer = OperateVnfRequestSerializer(data=request.data)
            if not operate_vnf_request_serializer.is_valid():
                raise NFLCMException(operate_vnf_request_serializer.errors)

            job_id = JobUtil.create_job('NF', 'OPERATE', instanceid)
            JobUtil.add_job_status(job_id, 0, "OPERATE_VNF_READY")
            self.operate_pre_check(instanceid, job_id)
            OperateVnf(operate_vnf_request_serializer.data, instanceid, job_id).start()
            response = Response(data={"jobId": job_id}, status=status.HTTP_202_ACCEPTED)
            # Location todo, it use job as the status storage
            # response["Location"] = "/api/vnflcm/v1/vnf_lcm_op_occs/%s" % lcmopoccid
            return response
        except NFLCMExceptionNotFound as e:
            probDetail = ProblemDetailsSerializer(data={"status": 404, "detail": "VNF Instance not found"})
            resp_isvalid = probDetail.is_valid()
            if not resp_isvalid:
                raise NFLCMException(probDetail.errors)
            return Response(data=probDetail.data, status=status.HTTP_404_NOT_FOUND)
        except NFLCMExceptionConflict as e:
            probDetail = ProblemDetailsSerializer(data={"status": 409, "detail": "VNF Instance not in Instantiated State"})
            resp_isvalid = probDetail.is_valid()
            if not resp_isvalid:
                raise NFLCMException(probDetail.errors)
            return Response(data=probDetail.data, status=status.HTTP_409_CONFLICT)
        except NFLCMException as e:
            logger.error(e.message)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': 'unexpected exception'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def operate_pre_check(self, nfInstId, jobId):
        vnf_insts = NfInstModel.objects.filter(nfinstid=nfInstId)
        if not vnf_insts.exists():
            raise NFLCMExceptionNotFound("VNF nf_inst_id does not exist.")

        if vnf_insts[0].status != 'INSTANTIATED':
            raise NFLCMExceptionConflict("VNF instantiationState is not INSTANTIATED.")
        NfInstModel.objects.filter(nfinstid=nfInstId).update(status=VNF_STATUS.OPERATING)

        JobUtil.add_job_status(jobId, 15, 'Nf operating pre-check finish')
        logger.info("Nf operating pre-check finish")
