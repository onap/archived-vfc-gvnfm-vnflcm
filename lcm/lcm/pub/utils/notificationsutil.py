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

import json
import logging
import requests

from rest_framework import status
from requests.auth import HTTPBasicAuth

from lcm.nf import const
from lcm.pub.database.models import SubscriptionModel

logger = logging.getLogger(__name__)


class NotificationsUtil(object):
    def __init__(self):
        pass

    def send_notification(self, notification):
        logger.info("Send Notifications to the callbackUri")
        filters = {
            "operationState": "operation_states",
            "operation": "operation_types"
        }
        subscriptions_filter = {v + "__contains": notification[k] for k, v in filters.iteritems()}

        subscriptions = SubscriptionModel.objects.filter(**subscriptions_filter)
        if not subscriptions.exists():
            logger.info("No subscriptions created for the filters %s" % notification)
            return
        logger.info("Start sending notifications")
        for subscription in subscriptions:
            # set subscription id
            notification["subscriptionId"] = subscription.subscription_id
            notification['_links']['subscription'] = {'href': '/api/vnflcm/v1/subscriptions/%s' % subscription.subscription_id}
            callbackUri = subscription.callback_uri
            auth_info = json.loads(subscription.auth_info)
            if auth_info["authType"] == const.OAUTH2_CLIENT_CREDENTIALS:
                pass
            try:
                self.post_notification(callbackUri, auth_info, notification)
            except Exception as e:
                logger.error("Failed to post notification: %s", e.message)

    def post_notification(self, callbackUri, auth_info, notification):
        params = auth_info.get("paramsBasic", {})
        username = params.get("userName")
        password = params.get("password")
        logger.info("Sending notification to %s", callbackUri)
        resp = requests.post(callbackUri, data=notification, auth=HTTPBasicAuth(username, password))
        if resp.status_code != status.HTTP_204_NO_CONTENT:
            raise Exception("Unable to send the notification to %s, due to %s" % (callbackUri, resp.text))
        return
