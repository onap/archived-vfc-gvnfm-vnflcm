# Copyright (C) 2018 Verizon. All Rights Reserved
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

import ast
import json
import logging
import traceback

from drf_yasg.utils import swagger_auto_schema
from lcm.nf.biz.create_subscription import CreateSubscription
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.nf.serializers.lccn_subscription_request import LccnSubscriptionRequestSerializer
from lcm.nf.serializers.lccn_subscription import LccnSubscriptionSerializer
from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)


class SubscriptionsView(APIView):
    @swagger_auto_schema(
        request_body=LccnSubscriptionRequestSerializer(),
        responses={
            status.HTTP_201_CREATED: LccnSubscriptionSerializer(),
            status.HTTP_303_SEE_OTHER: "",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    def post(self, request):
        logger.debug("SubscribeNotification--post::> %s" % request.data)
        try:
            lccn_subscription_request_serializer = LccnSubscriptionRequestSerializer(data=request.data)
            if not lccn_subscription_request_serializer.is_valid():
                raise NFLCMException(lccn_subscription_request_serializer.errors)
            subscription = CreateSubscription(
                lccn_subscription_request_serializer.data).do_biz()
            lccn_notifications_filter = {
                "notificationTypes": ast.literal_eval(subscription.notification_types),
                "operationTypes": ast.literal_eval(subscription.operation_types),
                "operationStates": ast.literal_eval(subscription.operation_states),
                "vnfInstanceSubscriptionFilter": json.loads(subscription.vnf_instance_filter)
            }
            subscription_data = {
                "id": subscription.subscription_id,
                "callbackUri": subscription.callback_uri,
                "_links": json.loads(subscription.links),
                "filter": lccn_notifications_filter
            }
            sub_resp_serializer = LccnSubscriptionSerializer(data=subscription_data)
            if not sub_resp_serializer.is_valid():
                raise NFLCMException(sub_resp_serializer.errors)
            return Response(data=sub_resp_serializer.data, status=status.HTTP_201_CREATED)
        except NFLCMException as e:
            logger.error(e.message)
            if "exists" in e.message:
                return Response(data={'error': '%s' % e.message}, status=status.HTTP_303_SEE_OTHER)
            return Response(data={'error': '%s' % e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            return Response(data={'error': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
