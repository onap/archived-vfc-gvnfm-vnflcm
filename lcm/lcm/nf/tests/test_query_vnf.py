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

from lcm.pub.database.models import (NfInstModel, VLInstModel,
                                     VNFCInstModel, VmInstModel, StorageInstModel)


class ResourceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.nf_inst_id = "01"
        NfInstModel.objects.all().delete()
        self.test_data_single_vnf = {
            "id": "1",
            "vnfInstanceName": "VNF1",
            "vnfProvider": None,
            "instantiationState": "INSTANTIATED",
            "instantiatedVnfInfo": {
                "vnfState": "STARTED",
                "extCpInfo": [],
                "virtualStorageResourceInfo": [
                    {
                        "id": "s02",
                        "storageResource": {
                            "resourceId": "resource01",
                            "vimConnectionId": "vim01"
                        }
                    }
                ],
                "extVirtualLinkInfo": [],
                "vnfcResourceInfo": [],
                "monitoringParameters": {},
                "flavourId": None,
                "vnfVirtualLinkResourceInfo": [],
                "scaleStatus": []
            },
            "vnfdVersion": None,
            "vnfPkgId": None
        }
        self.test_data_multi_vnf = [
            {
                "id": "1",
                "vnfInstanceName": "VNF1",
                "vnfProvider": None,
                "instantiationState": "INSTANTIATED",
                "instantiatedVnfInfo": {
                    "vnfState": "STARTED",
                    "extCpInfo": [],
                    "virtualStorageResourceInfo": [
                        {
                            "id": "s01",
                            "storageResource": {
                                "resourceId": "resource01",
                                "vimConnectionId": "vim01"
                            }
                        }
                    ],
                    "extVirtualLinkInfo": [],
                    "vnfcResourceInfo": [],
                    "monitoringParameters": {},
                    "flavourId": None,
                    "vnfVirtualLinkResourceInfo": [],
                    "scaleStatus": []
                },
                "vnfdVersion": None,
                "vnfPkgId": None
            },
            {
                "id": "2",
                "vnfInstanceName": "VNF2",
                "vnfProvider": None,
                "instantiationState": "INSTANTIATED",
                "instantiatedVnfInfo": {
                    "vnfState": "STARTED",
                    "extCpInfo": [],
                    "virtualStorageResourceInfo": [
                        {
                            "id": "s02",
                            "storageResource": {
                                "resourceId": "resource02",
                                "vimConnectionId": "vim02"
                            }
                        }
                    ],
                    "extVirtualLinkInfo": [],
                    "vnfcResourceInfo": [],
                    "monitoringParameters": {},
                    "flavourId": None,
                    "vnfVirtualLinkResourceInfo": [],
                    "scaleStatus": []
                },
                "vnfdVersion": None,
                "vnfPkgId": None
            }
        ]

    def tearDown(self):
        pass

    def test_get_vnf(self):
        vnf_inst_id = "1"
        NfInstModel(nfinstid=vnf_inst_id, nf_name='VNF1', status='INSTANTIATED').save()
        StorageInstModel(storageid='s02',
                         vimid='vim01',
                         resourceid='resource01',
                         insttype=1,
                         instid=vnf_inst_id).save()
        response = self.client.get("/api/vnflcm/v1/vnf_instances/%s" % vnf_inst_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_data_single_vnf, response.data)

    def test_get_vnf_not_exist(self):
        response = self.client.get("/api/vnflcm/v1/vnf_instances/x", format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual({'error': 'VnfInst(x) does not exist.'}, response.data)

    def test_get_vnf_net_not_exist(self):
        vnf_inst_id = "1"
        NfInstModel(nfinstid=vnf_inst_id, nf_name='VNF1', status='INSTANTIATED').save()
        VLInstModel(ownerid=vnf_inst_id, relatednetworkid='x', ownertype='0').save()
        response = self.client.get("/api/vnflcm/v1/vnf_instances/%s" % vnf_inst_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual({'error': 'NetworkInst(x) does not exist.'}, response.data)

    def test_get_vnf_vm_not_exist(self):
        vnf_inst_id = "1"
        NfInstModel(nfinstid=vnf_inst_id, nf_name='VNF1', status='INSTANTIATED').save()
        VNFCInstModel(instid=vnf_inst_id, vmid='x').save()
        response = self.client.get("/api/vnflcm/v1/vnf_instances/%s" % vnf_inst_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual({'error': 'VmInst(x) does not exist.'}, response.data)

    def test_get_vnf_storage_not_exist(self):
        vnf_inst_id = "1"
        NfInstModel(nfinstid=vnf_inst_id, nf_name='VNF1', status='INSTANTIATED').save()
        VNFCInstModel(instid=vnf_inst_id,
                      vmid='x',).save()
        VmInstModel(vmid='x', insttype='0').save()
        response = self.client.get("/api/vnflcm/v1/vnf_instances/%s" % vnf_inst_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_vnfs(self):
        for i in range(1, 3):
            NfInstModel(nfinstid='%s' % i,
                        nf_name='VNF%s' % i,
                        status='INSTANTIATED').save()
            StorageInstModel(storageid='s0%s' % i,
                             vimid='vim0%s' % i,
                             resourceid='resource0%s' % i,
                             insttype=1,
                             instid='%s' % i).save()
        response = self.client.get("/api/vnflcm/v1/vnf_instances", format='json')
        self.failUnlessEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.test_data_multi_vnf, response.data)

    def test_get_vnfs_not_exist(self):
        response = self.client.get("/api/vnflcm/v1/vnf_instances", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
