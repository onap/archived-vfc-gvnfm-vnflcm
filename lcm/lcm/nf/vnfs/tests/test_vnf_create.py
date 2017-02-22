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

import mock
from django.test import TestCase, Client
from rest_framework import status

from lcm.nf.vnfs.const import vnfd_rawdata
from lcm.nf.vnfs.vnf_create.inst_vnf import InstVnf
from lcm.pub.database.models import NfInstModel, JobStatusModel, VmInstModel, NetworkInstModel, \
    SubNetworkInstModel, PortInstModel
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.vimapi import adaptor
from lcm.pub.vimapi import api


class TestNFInstantiate(TestCase):
    def setUp(self):
        self.client = Client()
        VmInstModel.objects.create(vmid="1", vimid="1", resouceid="11", insttype=0, instid="1", vmname="test_01",
                                   operationalstate=1)
        VmInstModel.objects.create(vmid="2", vimid="2", resouceid="22", insttype=0, instid="2",
                                   vmname="test_02", operationalstate=1)
        NetworkInstModel.objects.create(networkid='1', vimid='1', resouceid='1', name='pnet_network',
                                        tenant='admin', insttype=0, instid='1')
        SubNetworkInstModel.objects.create(subnetworkid='1', vimid='1', resouceid='1', networkid='1',
                                           name='sub_pnet', tenant='admin', insttype=0, instid='1')
        PortInstModel.objects.create(portid='1', networkid='1', subnetworkid='1', vimid='1', resouceid='1',
                                     name='aaa_pnet_cp', tenant='admin', insttype=0, instid='1')

    def tearDown(self):
        pass
        VmInstModel.objects.all().delete()
        NetworkInstModel.objects.all().delete()
        SubNetworkInstModel.objects.all().delete()
        PortInstModel.objects.all().delete()

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(
            jobid=job_id,
            progress=job_progress,
            descp=job_detail)
        self.assertEqual(1, len(jobs))

    def test_swagger_ok(self):
        response = self.client.get("/openoapi/vnflcm/v1/swagger.json", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch.object(restcall, 'call_req')
    def test_create_vnf_identifier(self, mock_call_req):
        r1 = [0, json.JSONEncoder().encode({'package_id':'222', 'csar_id':'2222'}), '200']  # get csar_id from nslcm by vnfd_id
        r2 = [0, json.JSONEncoder().encode(vnfd_rawdata), '200']  # get rawdata from catalog by csar_id
        mock_call_req.side_effect = [r1, r2]
        data = {
            "vnfdId": "111",
            "vnfInstanceName": "vFW_01",
            "vnfInstanceDescription": "vFW in Nanjing TIC Edge"}
        response = self.client.post("/openoapi/vnflcm/v1/vnf_instances", data=data, format='json')
        self.failUnlessEqual(status.HTTP_201_CREATED, response.status_code)
        context = json.loads(response.content)
        self.assertTrue(NfInstModel.objects.filter(nfinstid=context['vnfInstanceId']).exists())

    @mock.patch.object(InstVnf, 'run')
    def test_instantiate_vnf(self, mock_run):
        mock_run.re.return_value = None
        response = self.client.post("/openoapi/vnflcm/v1/vnf_instances/12/instantiate", data={}, format='json')
        self.failUnlessEqual(status.HTTP_202_ACCEPTED, response.status_code)

    def test_instantiate_vnf_when_inst_id_not_exist(self):
        self.nf_inst_id = str(uuid.uuid4())
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
        data = inst_req_data
        InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        self.assert_job_result(self.job_id, 255, "VNF nf_inst_id is not exist.")

    @mock.patch.object(restcall, 'call_req')
    def test_instantiate_vnf_when_get_package_info_by_vnfdid_failed(self, mock_call_req):
        NfInstModel.objects.create(nfinstid='1111', nf_name='vFW_01', package_id='222',
                                   version='', vendor='', netype='', vnfd_model='', status='NOT_INSTANTIATED',
                                   nf_desc='vFW in Nanjing TIC Edge', vnfdid='111', create_time=now_time())
        r1 = [1, json.JSONEncoder().encode({'package_id':'222', 'csar_id':'2222'}), '200']  # get csar_id from nslcm by vnfd_id
        mock_call_req.side_effect = [r1]
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
        data = inst_req_data
        InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        self.assert_job_result(self.job_id, 255, "Failed to query package_info of vnfdid(111) from nslcm.")

    @mock.patch.object(restcall, 'call_req')
    def test_instantiate_vnf_when_get_rawdata_by_csarid_failed(self, mock_call_req):
        NfInstModel.objects.create(nfinstid='1111', nf_name='vFW_01', package_id='222',
                                   version='', vendor='', netype='', vnfd_model='', status='NOT_INSTANTIATED',
                                   nf_desc='vFW in Nanjing TIC Edge', vnfdid='111', create_time=now_time())
        r1 = [0, json.JSONEncoder().encode({'package_id':'222', 'csar_id':'2222'}), '200']  # get csar_id from nslcm by vnfd_id
        r2 = [1, json.JSONEncoder().encode(vnfd_rawdata), '200']  # get rawdata from catalog by csar_id
        mock_call_req.side_effect = [r1, r2]
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
        data = inst_req_data
        InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        self.assert_job_result(self.job_id, 255, "Failed to query rawdata of CSAR(2222) from catalog.")

    @mock.patch.object(restcall, 'call_req')
    def test_instantiate_vnf_when_applay_grant_failed(self, mock_call_req):
        NfInstModel.objects.create(nfinstid='1111', nf_name='vFW_01', package_id='222',
                                   version='', vendor='', netype='', vnfd_model='', status='NOT_INSTANTIATED',
                                   nf_desc='vFW in Nanjing TIC Edge', vnfdid='111', create_time=now_time())
        r1 = [0, json.JSONEncoder().encode({'package_id': '222', 'csar_id': '2222'}), '200']  # get csar_id from nslcm by vnfd_id
        r2 = [0, json.JSONEncoder().encode(vnfd_rawdata), '200']  # get rawdata from catalog by csar_id
        r3 = [1, json.JSONEncoder().encode({"vim":
                                                {
                                                    "vimid": '1',
                                                    "accessinfo": {"tenant": '2'}
                                                 }
                                            }), '200']  # apply_grant_to_nfvo
        mock_call_req.side_effect = [r1, r2, r3]
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
        data = inst_req_data
        InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        self.assert_job_result(self.job_id, 255, "Nf instancing apply grant exception")
    
    # @mock.patch.object(restcall, 'call_req')
    # @mock.patch.object(api, 'call')
    # def test_instantiate_vnf_when_(self, mock_call, mock_call_req):
    #     NfInstModel.objects.create(nfinstid='1111', nf_name='vFW_01', package_id='222',
    #                                version='', vendor='', netype='', vnfd_model='', status='NOT_INSTANTIATED',
    #                                nf_desc='vFW in Nanjing TIC Edge', vnfdid='111', create_time=now_time())
    #     r1 = [0, json.JSONEncoder().encode({'package_id': '222', 'csar_id': '2222'}), '200']  # get csar_id from nslcm by vnfd_id
    #     r2 = [0, json.JSONEncoder().encode(vnfd_rawdata), '200']  # get rawdata from catalog by csar_id
    #     r3 = [0, json.JSONEncoder().encode({"vim":{"vimid": '1', "accessinfo": {"tenant": '2'}}}), '200']  # apply_grant_to_nfvo
    #     mock_call_req.side_effect = [r1, r2, r3]
    #     c1_data = {  # get_tenant_id
    #         "tenants": [
    #             {
    #                 "id": "1",
    #                 "name": "tenantname_1"
    #             }
    #         ]
    #     }
    #     c2_data = {  # create_volume
    #         "id": "bc9eebdbbfd356458269340b9ea6fb73",
    #         "name": "volume1",
    #         # "returnCode": 1,
    #         "vimId": "vim_volume_1",
    #         "vimName": "vim_volume_1",
    #         "tenantId": "vim_volume_1",
    #         "volumeType": "123",
    #         "availabilityZone": "availabilityZone",
    #         "status": "avaluable"
    #     }
    #     c3_data = {  # get_volume
    #         "status": "available11",
    #         "name": "wangsong",
    #         "attachments": [
    #             {
    #                 "device": "/dev/vdc",
    #                 "serverId": "3030e666-528e-4954-88f5-cc21dab1262b",
    #                 "volumeId": "4bd3e9eb-cd8b-456a-8589-910836a0ab31",
    #                 "hostName": None,
    #                 "id": "4bd3e9eb-cd8b-456a-8589-910836a0ab31"
    #             }
    #         ],
    #         "createTime": "2015-12-02T06:39:40.000000",
    #         "type": None,
    #         "id": "4bd3e9eb-cd8b-456a-8589-910836a0ab31",
    #         "size": 40
    #     }
    #     mock_call.side_effect = [c1_data, c2_data, c3_data]
    #
    #     self.nf_inst_id = '1111'
    #     self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
    #     JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
    #     data = inst_req_data
    #     InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
    #     self.assert_job_result(self.job_id, 255, "unexpected exception")






    # @mock.patch.object(restcall, 'call_req')
    # @mock.patch.object(api, 'call')
    # def test_instantiate_vnf_when_111(self, mock_call, mock_call_req):
    #     NfInstModel.objects.create(nfinstid='1111', nf_name='vFW_01', package_id='222',
    #                                version='', vendor='', netype='', vnfd_model='', status='NOT_INSTANTIATED',
    #                                nf_desc='vFW in Nanjing TIC Edge', vnfdid='111', create_time=now_time())
    #     r1 = [0, json.JSONEncoder().encode({'package_id': '222', 'csar_id': '2222'}),
    #           '200']  # get csar_id from nslcm by vnfd_id
    #     r2 = [0, json.JSONEncoder().encode(vnfd_rawdata), '200']  # get rawdata from catalog by csar_id
    #     r3 = [0, json.JSONEncoder().encode({"vim": {"vimid": '1', "accessinfo": {"tenant": '2'}}}),
    #           '200']  # apply_grant_to_nfvo
    #     mock_call_req.side_effect = [r1, r2, r3]
    #     c1_data_get_tenant_id = {  # get_tenant_id
    #         "tenants": [
    #             {
    #                 "id": "1",
    #                 "name": "tenantname_1"
    #             }
    #         ]
    #     }
    #     c2_data_create_volume = {
    #         "id": "4bd3e9eb-cd8b-456a-8589-910836a0ab31",
    #         "name": "volume1",
    #         "returnCode": 1,
    #         "vimId": "vim_volume_1",
    #         "vimName": "vim_volume_1",
    #         "tenantId": "vim_volume_1",
    #         "volumeType": "123",
    #         "availabilityZone": "availabilityZone",
    #         "status": "availuable",
    #         "createTime": "2015-12-02T06:39:40.000000",
    #         "type": None,
    #         "size": 40
    #     }
    #     c3_data_get_volume = {  # get_volume
    #         "status": "available",
    #         "name": "wangsong",
    #         "attachments": [
    #             {
    #                 "device": "/dev/vdc",
    #                 "serverId": "3030e666-528e-4954-88f5-cc21dab1262b",
    #                 "volumeId": "4bd3e9eb-cd8b-456a-8589-910836a0ab31",
    #                 "hostName": None,
    #                 "id": "4bd3e9eb-cd8b-456a-8589-910836a0ab31"
    #             }
    #         ],
    #         "createTime": "2015-12-02T06:39:40.000000",
    #         "type": None,
    #         "id": "4bd3e9eb-cd8b-456a-8589-910836a0ab31",
    #         "size": 40
    #     }
    #     c4_data_create_network = {  # create_network
    #         "returnCode": 0,
    #         "vimId": "11111",
    #         "vimName": "11111",
    #         "status": "ACTIVE",
    #         "id": "3c9eebdbbfd345658269340b9ea6fb73",
    #         "name": "net1",
    #         "tenantId": "tenant1",
    #         "networkName": "ommnet",
    #         "shared": True,
    #         "vlanTransparent": True,
    #         "networkType": "vlan",
    #         "segmentationId": 202,
    #         "physicalNetwork": "ctrl",
    #         "routerExternal": False
    #     }
    #     c5_data_create_subnet = {
    #         "returnCode": 0,
    #         "vimId": "11111",
    #         "vimName": "11111",
    #         "status": " ACTIVE",
    #         "id": " d62019d3-bc6e-4319-9c1d-6722fc136a23",
    #         "tenantId": "tenant1",
    #         "networkId": "d32019d3-bc6e-4319-9c1d-6722fc136a22",
    #         "name": "subnet1",
    #         "cidr": "10.43.35.0/24",
    #         "ipVersion": 4,
    #         "enableDhcp": 1,
    #         "gatewayIp": "10.43.35.1",
    #         "dnsNameservers": [],
    #         "allocationPools": [
    #             {
    #                 "start": "192.168.199.2",
    #                 "end": "192.168.199.254"
    #             }
    #         ],
    #         "hostRoutes": []
    #     }
    #     mock_call.side_effect = [c1_data_get_tenant_id, c2_data_create_volume, c3_data_get_volume,
    #                              c4_data_create_network, c5_data_create_subnet]
    #
    #     self.nf_inst_id = '1111'
    #     self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
    #     JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
    #     data = inst_req_data
    #     InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
    #     self.assert_job_result(self.job_id, 255, "unexpected exception")




    # @mock.patch.object(restcall, 'call_req')
    # # @mock.patch.object(adaptor, 'create_vim_res')
    # def test_instantiate_vnf_when_create_res_failed(self, mock_call_req):
    #     NfvoRegInfoModel.objects.create(nfvoid='nfvo111', vnfminstid='vnfm111', apiurl='http://10.74.44.11',
    #                                     nfvouser='root', nfvopassword='root123')
    #     r1 = [0, json.JSONEncoder().encode(vnfd_model_dict), '200']
    #     r2 = [0, json.JSONEncoder().encode(vnfd_model_dict), '200']
    #     r3 = [0, json.JSONEncoder().encode('Nf instancing apply grant'), '200']
    #     # r4 = [0, json.JSONEncoder().encode('Nf instancing apply resource'), '200']
    #     mock_call_req.side_effect = [r1, r2, r3]
    #     # mock_create_vim_res.re.return_value = None
    #     create_data = {
    #         "vnfdId": "111",
    #         "vnfInstanceName": "vFW_01",
    #         "vnfInstanceDescription": " vFW in Nanjing TIC Edge"}
    #     self.nf_inst_id = CreateVnf(create_data).do_biz()
    #     self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
    #     JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
    #     data = inst_req_data
    #     InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
    #     self.assert_job_result(self.job_id, 255, "Create resource failed")

    # @mock.patch.object(restcall, 'call_req')
    # # @mock.patch.object(adaptor, 'create_vim_res')
    # def test_instantiate_vnf_success(self, mock_call_req):
    #     NfvoRegInfoModel.objects.create(nfvoid='nfvo111', vnfminstid='vnfm111', apiurl='http://10.74.44.11',
    #                                     nfvouser='root', nfvopassword='root123')
    #     r1 = [0, json.JSONEncoder().encode(vnfd_model_dict), '200']
    #     r2 = [0, json.JSONEncoder().encode(vnfd_model_dict), '200']
    #     r3 = [0, json.JSONEncoder().encode('Nf instancing apply grant'), '200']
    #     r4 = [0, json.JSONEncoder().encode('None'), '200']
    #     mock_call_req.side_effect = [r1, r2, r3, r4]
    #     # mock_create_vim_res.re.return_value = None
    #     create_data = {
    #         "vnfdId": "111",
    #         "vnfInstanceName": "vFW_01",
    #         "vnfInstanceDescription": " vFW in Nanjing TIC Edge"}
    #     self.nf_inst_id = CreateVnf(create_data).do_biz()
    #     self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
    #     JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
    #     data = inst_req_data
    #     InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
    #     self.assert_job_result(self.job_id, 100, "Instantiate Vnf success.")

inst_req_data = {
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
