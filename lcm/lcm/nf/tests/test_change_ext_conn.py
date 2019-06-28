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
import mock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from lcm.pub.database.models import NfInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.jobutil import JobUtil


class TestChangeExtConn(TestCase):
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
        NfInstModel(nfinstid='123',
                    nf_name='VNF1',
                    nf_desc="VNF DESC",
                    vnfdid="1",
                    netype="XGW",
                    vendor="ZTE",
                    vnfSoftwareVersion="V1",
                    version="V1",
                    package_id="2",
                    status='INSTANTIATED').save()
        self.req_data = {
            "extVirtualLinks": [{
                "id": "string",
                "resourceId": "329efb86-5cbb-4fc0-bc7c-6ea28f9d7389",
                "resourceSubnetId": "429efb86-5cbb-4fc0-bc7c-6ea28f9d7389",
                "extCps": [{
                    "cpdId": "ext_cp",
                    "cpConfig": [{
                        "cpInstanceId": "",
                        "cpProtocolData": [{
                            "layerProtocol": "IP_OVER_ETHERNET",
                            "ipOverEthernet": {
                                "ipAddresses": [{
                                    "type": "IPV4",
                                    "numDynamicAddresses": 0,
                                    "subnetId": "59e9ffa9-b67e-4c05-b191-ed179007536e"
                                }]
                            }
                        }]
                    }]
                }],
                "extLinkPorts": []
            }],
            "vimConnectionInfo": [{
                "id": "tecs_RegionOne",
                "vimType": "openstack",
                "vimId": "tecs_RegionOne",
                "accessInfo": {
                    "tenant": "admin"
                }
            }],
            "additionalParams": {
                "vmid": "552ea058-6441-4de5-b4c1-b0a52c7557e8"
            }
        }

    def tearDown(self):
        NfInstModel.objects.filter(nfinstid='12345').delete()
        NfInstModel.objects.filter(nfinstid='123').delete()

    def test_change_ext_conn_not_found(self):
        url = "/api/vnflcm/v1/vnf_instances/12/change_ext_conn"
        response = self.client.post(url,
                                    data=self.req_data,
                                    format='json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_change_ext_conn_conflict(self):
        url = "/api/vnflcm/v1/vnf_instances/12345/change_ext_conn"
        response = self.client.post(url,
                                    data=self.req_data,
                                    format='json')
        self.assertEqual(status.HTTP_409_CONFLICT, response.status_code)

    def test_change_ext_conn_badreq(self):
        url = "/api/vnflcm/v1/vnf_instances/123/change_ext_conn"
        response = self.client.post(url,
                                    data={},
                                    format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock.patch.object(JobUtil, 'create_job')
    def test_change_ext_conn_inner_error(self, mock_run):
        mock_run.return_value = NFLCMException('Boom!')
        url = "/api/vnflcm/v1/vnf_instances/123/change_ext_conn"
        response = self.client.post(url,
                                    data=self.req_data,
                                    format='json')
        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)
