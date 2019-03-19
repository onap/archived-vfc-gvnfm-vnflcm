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

from django.test import TestCase, Client
from rest_framework import status

from lcm.pub.database.models import SubscriptionModel


class TestQuerySubscriptions(TestCase):
    def setUp(self):
        self.client = Client()
        self.subscription_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        self.vnf_instance_id = "cd552c9c-ab6f-11e8-b354-236c32aa91a1"
        SubscriptionModel.objects.all().delete()
        self.test_single_subscription = {
            "id": self.subscription_id,
            "callbackUri": "http://aurl.com",
            "_links": {
                "self": {
                    "href": "/api/v1/subscriptions/99442b18-a5c7-11e8-998c-bf1755941f16"
                }
            },
            "filter": {
                "notificationTypes": ["VnfLcmOperationOccurrenceNotification"],
                "operationTypes": ["INSTANTIATE"],
                "operationStates": ["STARTING"],
                "vnfInstanceSubscriptionFilter": {
                    "vnfdIds": [],
                    "vnfInstanceIds": [self.vnf_instance_id],
                    "vnfInstanceNames": [],
                    "vnfProductsFromProviders": {
                        "vnfProvider": "vendor"
                    }
                }

            }
        }

    def tearDown(self):
        pass

    def test_get_subscriptions(self):
        vnf_instance_filter = {
            "vnfdIds": [],
            "vnfInstanceIds": [self.vnf_instance_id],
            "vnfInstanceNames": [],
            "vnfProductsFromProviders": {
                "vnfProvider": "vendor"
            }
        }
        links = {
            "self": {
                "href": "/api/v1/subscriptions/99442b18-a5c7-11e8-998c-bf1755941f16"
            }
        }
        SubscriptionModel(subscription_id=self.subscription_id, callback_uri="http://aurl.com",
                          auth_info="{}", notification_types="['VnfLcmOperationOccurrenceNotification']",
                          operation_types="['INSTANTIATE']",
                          operation_states="['STARTING']",
                          links=json.dumps(links),
                          vnf_instance_filter=json.dumps(vnf_instance_filter)).save()
        response = self.client.get("/api/vnflcm/v1/subscriptions", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([self.test_single_subscription], response.data)

    def test_get_subscriptions_with_vnf_instance_id(self):
        vnf_instance_filter = {
            "vnfdIds": [],
            "vnfInstanceIds": [self.vnf_instance_id],
            "vnfInstanceNames": [],
            "vnfProductsFromProviders": {
                "vnfProvider": "vendor"
            }
        }
        links = {
            "self": {
                "href": "/api/v1/subscriptions/99442b18-a5c7-11e8-998c-bf1755941f16"
            }
        }
        SubscriptionModel(subscription_id=self.subscription_id, callback_uri="http://aurl.com",
                          auth_info="{}", notification_types="['VnfLcmOperationOccurrenceNotification']",
                          operation_types="['INSTANTIATE']",
                          operation_states="['STARTING']",
                          links=json.dumps(links),
                          vnf_instance_filter=json.dumps(vnf_instance_filter)).save()
        dummy_vnf_id = "584b35e2-b2a2-11e8-8e11-645106374fd3"
        dummy_subscription_id = "947dcd2c-b2a2-11e8-b365-645106374fd4"
        vnf_instance_filter["vnfInstanceIds"].append(dummy_vnf_id)
        SubscriptionModel(subscription_id=dummy_subscription_id, callback_uri="http://aurl.com",
                          auth_info="{}", notification_types="['VnfLcmOperationOccurrenceNotification']",
                          operation_types="['INSTANTIATE']",
                          operation_states="['STARTING']",
                          links=json.dumps(links),
                          vnf_instance_filter=json.dumps(vnf_instance_filter)).save()
    
        response = self.client.get("/api/vnflcm/v1/subscriptions?vnfInstanceId=" + dummy_vnf_id, format='json')
        expected_response = self.test_single_subscription.copy()
        expected_response["id"] = dummy_subscription_id
        expected_response["filter"]["vnfInstanceSubscriptionFilter"]["vnfInstanceIds"] = \
            vnf_instance_filter["vnfInstanceIds"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([expected_response], response.data)

    def test_get_subscriptions_with_unknown_vnf_instance_id(self):
        vnf_instance_filter = {
            "vnfdIds": [],
            "vnfInstanceIds": [self.vnf_instance_id],
            "vnfInstanceNames": [],
            "vnfProductsFromProviders": {
                "vnfProvider": "vendor"
            }
        }
        links = {
            "self": {
                "href": "/api/v1/subscriptions/99442b18-a5c7-11e8-998c-bf1755941f16"
            }
        }
        SubscriptionModel(subscription_id=self.subscription_id, callback_uri="http://aurl.com",
                          auth_info="{}", notification_types="['VnfLcmOperationOccurrenceNotification']",
                          operation_types="['INSTANTIATE']",
                          operation_states="['STARTING']",
                          links=json.dumps(links),
                          vnf_instance_filter=json.dumps(vnf_instance_filter)).save()
        response = self.client.get("/api/vnflcm/v1/subscriptions?vnfInstanceId=dummy", format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_subscriptions_with_invalid_filter(self):
        vnf_instance_filter = {
            "vnfdIds": [],
            "vnfInstanceIds": [self.vnf_instance_id],
            "vnfInstanceNames": [],
            "vnfProductsFromProviders": {
                "vnfProvider": "vendor"
            }
        }
        links = {
            "self": {
                "href": "/api/v1/subscriptions/99442b18-a5c7-11e8-998c-bf1755941f16"
            }
        }
        SubscriptionModel(subscription_id=self.subscription_id, callback_uri="http://aurl.com",
                          auth_info="{}", notification_types="['VnfLcmOperationOccurrenceNotification']",
                          operation_types="['INSTANTIATE']",
                          operation_states="['STARTING']",
                          links=json.dumps(links),
                          vnf_instance_filter=json.dumps(vnf_instance_filter)).save()
        response = self.client.get("/api/vnflcm/v1/subscriptions?dummy=dummy", format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_subscriptions_with_operation_type_filter(self):
        vnf_instance_filter = {
            "vnfdIds": [],
            "vnfInstanceIds": [self.vnf_instance_id],
            "vnfInstanceNames": [],
            "vnfProductsFromProviders": {
                "vnfProvider": "vendor"
            }
        }
        links = {
            "self": {
                "href": "/api/v1/subscriptions/99442b18-a5c7-11e8-998c-bf1755941f16"
            }
        }
        SubscriptionModel(subscription_id=self.subscription_id, callback_uri="http://aurl.com",
                          auth_info="{}", notification_types="['VnfLcmOperationOccurrenceNotification']",
                          operation_types="['INSTANTIATE']",
                          operation_states="['STARTING']",
                          links=json.dumps(links),
                          vnf_instance_filter=json.dumps(vnf_instance_filter)).save()
        dummy_vnf_id = "584b35e2-b2a2-11e8-8e11-645106374fd3"
        dummy_subscription_id = "947dcd2c-b2a2-11e8-b365-645106374fd4"
        vnf_instance_filter["vnfInstanceIds"].append(dummy_vnf_id)
        SubscriptionModel(subscription_id=dummy_subscription_id, callback_uri="http://aurl.com",
                          auth_info="{}", notification_types="['VnfLcmOperationOccurrenceNotification']",
                          operation_types="['SCALE']",
                          operation_states="['STARTING']",
                          links=json.dumps(links),
                          vnf_instance_filter=json.dumps(vnf_instance_filter)).save()
    
        response = self.client.get("/api/vnflcm/v1/subscriptions?operationTypes=SCALE", format='json')
        expected_response = self.test_single_subscription.copy()
        expected_response["id"] = dummy_subscription_id
        expected_response["filter"]["vnfInstanceSubscriptionFilter"]["vnfInstanceIds"] = \
            vnf_instance_filter["vnfInstanceIds"]
        expected_response["filter"]["operationTypes"] = ["SCALE"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([expected_response], response.data)
