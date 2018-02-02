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
from rest_framework.views import APIView
from rest_framework.response import Response
from .resources import ResCreateThread, ResDeleteThread

logger = logging.getLogger(__name__)


class SampleList(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: 'Successfully'})
    def get(self, request, format=None):
        logger.debug("get")
        return Response({"status": "active"})


class ResourceList(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: 'Successfully'})
    def post(self, request, action_type):
        logger.debug("ResourceList post(%s): %s", action_type, request.data)
        if action_type == "inst":
            ResCreateThread(request.data).start()
        else:
            ResDeleteThread(request.data).start()
        return Response(data=None, status=status.HTTP_204_NO_CONTENT)
