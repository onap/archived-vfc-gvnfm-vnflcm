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
from django.test import TestCase, Client
from rest_framework import status

from lcm.pub.database.models import NfInstModel, StorageInstModel


class ResourceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.nf_inst_id = "01"
        NfInstModel.objects.all().delete()
        self.test_data = {
            "vnfInstanceId": "1",
            "vnfInstanceName": "VNF1",
            "vnfProvider": None,
            "instantiatedVnfInfo": {
                "vnfState": None,
                "extCpInfo": [],
                "virtualStorageResourceInfo": [
                    {
                        "virtualStorageInstanceId": "s02",
                        "storageResource": {
                            "resourceId": "resource01",
                            "vimId": "vim01"
                        }
                    }
                ],
                "extVirtualLink": [],
                "vnfcResourceInfo": [],
                "monitoringParameters": {},
                "vimInfo": [],
                "flavourId": None,
                "virtualLinkResourceInfo": [],
                "scaleStatus": []
            },
            "vnfdVersion": None,
            "onboardedVnfPkgInfoId": None
        }

    def tearDown(self):
        pass

    def test_get_vnf(self):
        vnf_inst_id = "1"
        NfInstModel(nfinstid=vnf_inst_id, nf_name='VNF1').save()
        StorageInstModel(storageid='s02', vimid='vim01', resouceid='resource01', insttype=1, \
                         instid=vnf_inst_id).save()
        response = self.client.get("/openoapi/vnflcm/v1/vnf_instances/%s" % vnf_inst_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_data, response.data)