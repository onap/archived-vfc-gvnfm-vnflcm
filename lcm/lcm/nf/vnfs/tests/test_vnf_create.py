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

import json
import uuid

from django.test import TestCase, Client
from rest_framework import status

from lcm.pub.database.models import VnfInstModel


class TestNsInstantiate(TestCase):
    def setUp(self):
        self.client = Client()
        self.nsd_id = str(uuid.uuid4())

    def tearDown(self):
        pass

    def test_create_vnf_identifier(self):
        data = {
            "vnfdId": "zte_vFW_51610",
            "vnfInstanceName": "vFW_01",
            "vnfInstanceDescription": " vFW in Nanjing TIC Edge"}
        response = self.client.post("/gvnfmapi/lcm/v1/vnf_instances", data=data, format='json')
        self.failUnlessEqual(status.HTTP_201_CREATED, response.status_code)
        context = json.loads(response.content)
        self.assertTrue(VnfInstModel.objects.filter(id=context['vnfInstanceId']).exists())
