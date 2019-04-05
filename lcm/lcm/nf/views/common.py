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

from rest_framework import status
from rest_framework.response import Response

from lcm.pub.exceptions import NFLCMException
from lcm.pub.exceptions import NFLCMExceptionPreconditionFailed
from lcm.pub.exceptions import NFLCMExceptionBadRequest
from lcm.pub.exceptions import NFLCMExceptionNotFound
from lcm.pub.exceptions import NFLCMExceptionConflict
from lcm.pub.exceptions import NFLCMExceptionSeeOther

logger = logging.getLogger(__name__)


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
