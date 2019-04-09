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


class TestNfScaleToLevel(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.req_data = {
            "instantiationLevelId": "instantiation_level_2",
            "scaleInfo": []
        }

    def tearDown(self):
        pass

    def test_scale_vnf_to_level_not_found(self):
        url = "/api/vnflcm/v1/vnf_instances/12/scale_to_level"
        response = self.client.post(url,
                                    data=self.req_data,
                                    format='json')
        self.failUnlessEqual(status.HTTP_404_NOT_FOUND, response.status_code)
