# Copyright (C) 2019 ZTE. All Rights Reserved.
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
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from lcm.pub.database.models import NfInstModel


class TestNfScale(TestCase):
    def setUp(self):
        self.client = APIClient()
        NfInstModel(nfinstid='12345',
                    nf_name='VNF1',
                    nf_desc="VNF DESC",
                    vnfdid="1",
                    netype="XGW",
                    vendor="ZTE",
                    vnfSoftwareVersion="V1",
                    version="V1",
                    package_id="2",
                    status='NOT_INSTANTIATED').save()
        self.req_data = {
            "type": "SCALE_IN",
            "aspectId": "sunshine_aspect"
        }

    def tearDown(self):
        NfInstModel.objects.filter(nfinstid='12345').delete()

    def test_scale_vnf_not_found(self):
        url = "/api/vnflcm/v1/vnf_instances/12/scale"
        response = self.client.post(url,
                                    data=self.req_data,
                                    format='json')
        self.failUnlessEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_scale_vnf_conflict(self):
        url = "/api/vnflcm/v1/vnf_instances/12345/scale"
        response = self.client.post(url,
                                    data=self.req_data,
                                    format='json')
        self.failUnlessEqual(status.HTTP_409_CONFLICT, response.status_code)
