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

from lcm.nf.vnfs.vnf_create.inst_vnf import InstVnf
from lcm.pub.database.models import NfInstModel, JobStatusModel, VmInstModel, NetworkInstModel, \
    SubNetworkInstModel, PortInstModel
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time


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
        r2 = [0, json.JSONEncoder().encode(vnfd_raw_data), '200']  # get rawdata from catalog by csar_id
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
        r2 = [1, json.JSONEncoder().encode(vnfd_raw_data), '200']  # get rawdata from catalog by csar_id
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
        r2 = [0, json.JSONEncoder().encode(vnfd_raw_data), '200']  # get rawdata from catalog by csar_id
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
    # def test_instantiate_vnf_when_(self, mock_call_req):
    #     NfInstModel.objects.create(nfinstid='1111', nf_name='vFW_01', package_id='222',
    #                                version='', vendor='', netype='', vnfd_model='', status='NOT_INSTANTIATED',
    #                                nf_desc='vFW in Nanjing TIC Edge', vnfdid='111', create_time=now_time())
    #     r1 = [0, json.JSONEncoder().encode({'package_id': '222', 'csar_id': '2222'}),
    #           '200']  # get csar_id from nslcm by vnfd_id
    #     r2 = [0, json.JSONEncoder().encode(vnfd_raw_data), '200']  # get rawdata from catalog by csar_id
    #     r3 = [0, json.JSONEncoder().encode({"vim":{"vimid": '1', "accessinfo": {"tenant": '2'}}}), '200']  # apply_grant_to_nfvo
    #     mock_call_req.side_effect = [r1, r2, r3]
    #     self.nf_inst_id = '1111'
    #     self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
    #     JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
    #     data = inst_req_data
    #     InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
    #     self.assert_job_result(self.job_id, 255, "Nf instancing apply grant exception")



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

vnfd_model_dict = {
    'local_storages': [],
    'vdus': [
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'2'},
            'local_storages': [],
            'vdu_id': u'vdu_omm.001',
            'image_file': u'opencos_sss_omm_img_release_20150723-1-disk1',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'omm.001',
                'manual_scale_select_vim': False},
            'description': u'singleommvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'4'},
            'local_storages': [],
            'vdu_id': u'vdu_1',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'1',
                'manual_scale_select_vim': False},
            'description': u'ompvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_2',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'2',
                'manual_scale_select_vim': False},
            'description': u'ompvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_3',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'3',
                'manual_scale_select_vim': False},
            'description': u'ompvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'4'},
            'local_storages': [],
            'vdu_id': u'vdu_10',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'10',
                'manual_scale_select_vim': False},
            'description': u'ppvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_11',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'11',
                'manual_scale_select_vim': False},
            'description': u'ppvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_12',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'12',
                'manual_scale_select_vim': False},
            'description': u'ppvm'}],
    'volumn_storages': [],
    'policies': {
        'scaling': {
            'targets': {},
            'policy_id': u'policy_scale_sss-vnf-template',
            'properties': {
                'policy_file': '*-vnfd.zip/*-vnf-policy.xml'},
            'description': ''}},
    'image_files': [
        {
            'description': '',
            'properties': {
                'name': u'opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'checksum': '',
                'disk_format': u'VMDK',
                'file_url': u'./zte-cn-sss-main-image/OMM/opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'},
            'image_file_id': u'opencos_sss_omm_img_release_20150723-1-disk1'},
        {
            'description': '',
            'properties': {
                'name': u'sss.vmdk',
                'checksum': '',
                'disk_format': u'VMDK',
                'file_url': u'./zte-cn-sss-main-image/NE/sss.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'},
            'image_file_id': u'sss'}],
    'vls': [],
    'cps': [],
    'metadata': {
        'vendor': u'zte',
        'is_shared': False,
        'description': '',
        'domain_type': u'CN',
        'version': u'v4.14.10',
        'vmnumber_overquota_alarm': False,
        'cross_dc': False,
        'vnf_type': u'SSS',
        'vnfd_version': u'V00000001',
        'id': u'sss-vnf-template',
        'name': u'sss-vnf-template'},
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

vnfd_raw_data = {
    "rawData": {
        "instance": {
            "metadata": {
                "is_shared": False,
                "plugin_info": "vbrasplugin_1.0",
                "vendor": "zte",
                "request_reclassification": False,
                "name": "vbras",
                "version": 1,
                "vnf_type": "vbras",
                "cross_dc": False,
                "vnfd_version": "1.0.0",
                "id": "zte_vbras_1.0",
                "nsh_aware": True
            },
            "nodes": [
                {
                    "id": "aaa_dnet_cp_0xu2j5sbigxc8h1ega3if0ld1",
                    "type_name": "tosca.nodes.nfv.ext.zte.CP",
                    "template_name": "aaa_dnet_cp",
                    "properties": {
                        "bandwidth": {
                            "type_name": "integer",
                            "value": 0
                        },
                        "direction": {
                            "type_name": "string",
                            "value": "bidirectional"
                        },
                        "vnic_type": {
                            "type_name": "string",
                            "value": "normal"
                        },
                        "sfc_encapsulation": {
                            "type_name": "string",
                            "value": "mac"
                        },
                        "order": {
                            "type_name": "integer",
                            "value": 2
                        }
                    },
                    "relationships": [
                        {
                            "name": "guest_os",
                            "source_requirement_index": 0,
                            "target_node_id": "AAA_image_d8aseebr120nbm7bo1ohkj194",
                            "target_capability_name": "feature"
                        }
                    ]
                },
                {
                    "id": "LB_Image_oj5l2ay8l2g6vcq6fsswzduha",
                    "type_name": "tosca.nodes.nfv.ext.ImageFile",
                    "template_name": "LB_Image",
                    "properties": {
                        "disk_format": {
                            "type_name": "string",
                            "value": "qcow2"
                        },
                        "file_url": {
                            "type_name": "string",
                            "value": "/SoftwareImages/image-lb"
                        },
                        "name": {
                            "type_name": "string",
                            "value": "image-lb"
                        }
                    }
                }
            ]
        },
        "model": {
            "metadata": {
                "is_shared": False,
                "plugin_info": "vbrasplugin_1.0",
                "vendor": "zte",
                "request_reclassification": False,
                "name": "vbras",
                "version": 1,
                "vnf_type": "vbras",
                "cross_dc": False,
                "vnfd_version": "1.0.0",
                "id": "zte_vbras_1.0",
                "nsh_aware": True
            },
            "node_templates": [
                {
                    "name": "aaa_dnet_cp",
                    "type_name": "tosca.nodes.nfv.ext.zte.CP",
                    "default_instances": 1,
                    "min_instances": 0,
                    "properties": {
                        "bandwidth": {
                            "type_name": "integer",
                            "value": 0
                        }
                    },
                    "requirement_templates": [
                        {
                            "name": "virtualbinding",
                            "target_node_template_name": "AAA",
                            "target_capability_name": "virtualbinding"
                        }
                    ]
                }
            ]
        }
    }
}
