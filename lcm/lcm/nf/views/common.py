# Copyright 2019 ZTE Corporation.
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

import traceback
import logging
import uuid

from rest_framework import status
from rest_framework.response import Response

from lcm.pub.exceptions import NFLCMException
from lcm.pub.exceptions import NFLCMExceptionPreconditionFailed
from lcm.pub.exceptions import NFLCMExceptionBadRequest
from lcm.pub.exceptions import NFLCMExceptionNotFound
from lcm.pub.exceptions import NFLCMExceptionConflict
from lcm.pub.exceptions import NFLCMExceptionSeeOther
from lcm.pub.database.models import NfInstModel
from lcm.pub.utils.jobutil import JobUtil
from lcm.nf.const import OPERATION_TYPE

logger = logging.getLogger(__name__)

CACHE_ETAG = None


def make_error_resp(status, detail):
    return Response(
        data={
            'status': status,
            'detail': detail
        },
        status=status
    )


def view_safe_call_with_log(logger):
    def view_safe_call(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except NFLCMExceptionSeeOther as e:
                logger.error(e.message)
                resp = Response(status=status.HTTP_303_SEE_OTHER)
                resp["Location"] = ""
                # resp["Location"] = "subscriptions/%s" % e.id
                return resp
            except NFLCMExceptionNotFound as e:
                logger.error(e.message)
                return make_error_resp(
                    detail=e.message,
                    status=status.HTTP_404_NOT_FOUND
                )
            except NFLCMExceptionBadRequest as e:
                logger.error(e.message)
                return make_error_resp(
                    detail=e.message,
                    status=status.HTTP_400_BAD_REQUEST
                )
            except NFLCMExceptionConflict as e:
                logger.error(e.message)
                return make_error_resp(
                    detail=e.message,
                    status=status.HTTP_409_CONFLICT
                )
            except NFLCMExceptionPreconditionFailed as e:
                logger.error(e.message)
                return make_error_resp(
                    detail=e.message,
                    status=status.HTTP_412_PRECONDITION_FAILED
                )
            except NFLCMException as e:
                logger.error(e.message)
                return make_error_resp(
                    detail=e.message,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                logger.error(e.message)
                logger.error(traceback.format_exc())
                return make_error_resp(
                    detail='Unexpected exception',
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return wrapper
    return view_safe_call


def deal_vnf_action(logger, opt_type, opt_status, instid, req, req_serializer, act_task):
    logger.debug("%s--post::> %s, %s", opt_type, instid, req.data)

    act_vnf_req_serializer = req_serializer(data=req.data)
    if not act_vnf_req_serializer.is_valid():
        raise NFLCMException(act_vnf_req_serializer.errors)

    vnf_insts = NfInstModel.objects.filter(nfinstid=instid)
    if not vnf_insts.exists():
        raise NFLCMExceptionNotFound("VNF(%s) does not exist." % instid)

    if opt_type == OPERATION_TYPE.INSTANTIATE:
        if vnf_insts[0].status == 'INSTANTIATED':
            raise NFLCMExceptionConflict("VNF(%s) is already INSTANTIATED." % instid)
    elif opt_type != OPERATION_TYPE.MODIFY_INFO:
        if vnf_insts[0].status != 'INSTANTIATED':
            raise NFLCMExceptionConflict("VNF(%s) is not INSTANTIATED." % instid)

    job_id = JobUtil.create_job('NF', opt_type, instid)
    JobUtil.add_job_status(job_id, 0, "VNF_%s_READY" % opt_type)

    vnf_insts.update(status=opt_status)
    act_task(req.data, instid, job_id).start()

    return Response(data={"jobId": job_id}, status=status.HTTP_202_ACCEPTED)


def deal_indivdual_query(res_serializer, query_fun, *args):
    global CACHE_ETAG

    res = query_fun(*args)
    resp_serializer = res_serializer(data=res)
    if not resp_serializer.is_valid():
        raise NFLCMException(resp_serializer.errors)

    resp = Response(data=resp_data, status=status.HTTP_200_OK)
    if res_serializer == VnfInstanceSerializer:
        CACHE_ETAG = "%s" % uuid.uuid1()
        logger.debug("set CACHE_ETAG = %s", CACHE_ETAG)
        resp["ETag"] = CACHE_ETAG
    return resp
