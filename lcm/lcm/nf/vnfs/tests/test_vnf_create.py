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

    def test_instantiate_vnf(self):
        data = {
            "flavourId": "flavour_1",
            "instantiationLevelId": "instantiationLevel_1",
            "extVirtualLinks": [
                {
                    "vlInstanceId": "1",
                    "vim": {
                        "vimInfoId": "1",
                        "vimId": "1",
                        "interfaceInfo": {
                            "vimType": "vim",
                            "apiVersion": "v2",
                            "protocolType": "http"
                        },
                        "accessInfo": {
                            "tenant": "tenant_vCPE",
                            "username": "vCPE",
                            "password": "vCPE_321"
                        },
                        "interfaceEndpoint": "http://10.43.21.105:80/"
                    },
                    "resourceId": "1246",
                    "extCps": [
                        {
                            "cpdId": "11",
                            "addresses": [
                                {
                                    "addressType": "MAC",
                                    "l2AddressData": "00:f3:43:20:a2:a3"
                                },
                                {
                                    "addressType": "IP",
                                    "l3AddressData": {
                                        "iPAddressType": "IPv4",
                                        "iPAddress": "192.168.104.2"
                                    }
                                }
                            ],
                            "numDynamicAddresses": 0
                        }
                    ]
                }
            ],
            "localizationLanguage": "en_US",
            "additionalParams": {}
        }
        response = self.client.post("/gvnfmapi/lcm/v1/vnf_instances/12/instantiate", data=data, format='json')
        self.failUnlessEqual(status.HTTP_202_ACCEPTED, response.status_code)
