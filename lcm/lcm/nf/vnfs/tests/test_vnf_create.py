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

from lcm.nf.vnfs.const import vnfd_rawdata, c1_data_get_tenant_id, c4_data_create_network, c2_data_create_volume, \
    c5_data_create_subnet, c3_data_get_volume, c6_data_create_port, c7_data_create_flavor, c8_data_list_image, \
    c9_data_create_vm, c10_data_get_vm, inst_req_data
from lcm.nf.vnfs.vnf_create.inst_vnf import InstVnf
from lcm.pub.database.models import NfInstModel, JobStatusModel
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.vimapi import api


class TestNFInstantiate(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

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
        r1_get_csarid_by_vnfdid = [0, json.JSONEncoder().encode([{'package_id': '222', 'csar_id': '2222','vnfd_id':'111'}]), '200']
        r2_get_rawdata_from_catalog = [0, json.JSONEncoder().encode(vnfd_rawdata), '200']
        mock_call_req.side_effect = [r1_get_csarid_by_vnfdid, r2_get_rawdata_from_catalog]
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
        jobs = JobStatusModel.objects.filter(
            jobid=self.job_id,
            progress=0,
            descp="INST_VNF_READY")
        self.assertEqual(1, len(jobs))
        data = inst_req_data
        InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        self.assert_job_result(self.job_id, 255, "VNF nf_inst_id is not exist.")

    @mock.patch.object(restcall, 'call_req')
    def test_instantiate_vnf_when_get_package_info_by_vnfdid_failed(self, mock_call_req):
        NfInstModel.objects.create(nfinstid='1111', nf_name='vFW_01', package_id='222',
                                   version='', vendor='', netype='', vnfd_model='', status='NOT_INSTANTIATED',
                                   nf_desc='vFW in Nanjing TIC Edge', vnfdid='111', create_time=now_time())
        r1_get_csarid_by_vnfdid = [1, json.JSONEncoder().encode([{'package_id': '222', 'csar_id': '2222','vnfd_id':'111'}]), '200']
        mock_call_req.side_effect = [r1_get_csarid_by_vnfdid]
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
        r1_get_csarid_by_vnfdid = [0, json.JSONEncoder().encode([{'package_id': '222', 'csar_id': '2222','vnfd_id':'111'}]), '200']
        r2_get_rawdata_from_catalog = [1, json.JSONEncoder().encode(vnfd_rawdata), '200']
        mock_call_req.side_effect = [r1_get_csarid_by_vnfdid, r2_get_rawdata_from_catalog]
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
        r1_get_csarid_by_vnfdid = [0, json.JSONEncoder().encode([{'package_id': '222', 'csar_id': '2222','vnfd_id':'111'}]), '200']
        r2_get_rawdata_from_catalog = [0, json.JSONEncoder().encode(vnfd_rawdata), '200']
        r3_apply_grant_result = [1, json.JSONEncoder().encode(
            {"vim": {"vimid": 'vimid_1', "accessinfo": {"tenant": 'tenantname_1'}}}), '200']
        mock_call_req.side_effect = [r1_get_csarid_by_vnfdid, r2_get_rawdata_from_catalog, r3_apply_grant_result]
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
        data = inst_req_data
        InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        self.assert_job_result(self.job_id, 255, "Nf instancing apply grant exception")

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_instantiate_vnf_when_(self, mock_call, mock_call_req):
        NfInstModel.objects.create(nfinstid='1111', nf_name='vFW_01', package_id='222',
                                   version='', vendor='', netype='', vnfd_model='', status='NOT_INSTANTIATED',
                                   nf_desc='vFW in Nanjing TIC Edge', vnfdid='111', create_time=now_time())
        r1_get_csarid_by_vnfdid = [0, json.JSONEncoder().encode([{'package_id': '222', 'csar_id': '2222','vnfd_id':'111'}]), '200']
        r2_get_rawdata_from_catalog = [0, json.JSONEncoder().encode(vnfd_rawdata), '200']
        r3_apply_grant_result = [0, json.JSONEncoder().encode(
            {"vim": {"vimid": 'vimid_1', "accessinfo": {"tenant": 'tenantname_1'}}}), '200']
        mock_call_req.side_effect = [r1_get_csarid_by_vnfdid, r2_get_rawdata_from_catalog, r3_apply_grant_result]
        mock_call.side_effect = [c1_data_get_tenant_id, c2_data_create_volume, c3_data_get_volume]
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
        data = inst_req_data
        InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        self.assert_job_result(self.job_id, 255, "unexpected exception")

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_instantiate_vnf_success(self, mock_call, mock_call_req):
        NfInstModel.objects.create(nfinstid='1111', nf_name='vFW_01', package_id='222',
                                   version='', vendor='', netype='', vnfd_model='', status='NOT_INSTANTIATED',
                                   nf_desc='vFW in Nanjing TIC Edge', vnfdid='111', create_time=now_time())
        r1_get_csarid_by_vnfdid = [0, json.JSONEncoder().encode([{'package_id': '222', 'csar_id': '2222','vnfd_id':'111'}]), '200']
        r2_get_rawdata_from_catalog = [0, json.JSONEncoder().encode(vnfd_rawdata), '200']
        r3_apply_grant_result = [0, json.JSONEncoder().encode(
            {"vim": {"vimid": 'vimid_1', "accessinfo": {"tenant": 'tenantname_1'}}}), '200']
        r4_lcm_notify_result = [0, json.JSONEncoder().encode(''), '200']
        mock_call_req.side_effect = [r1_get_csarid_by_vnfdid, r2_get_rawdata_from_catalog,
                                     r3_apply_grant_result, r4_lcm_notify_result]
        mock_call.side_effect = [c1_data_get_tenant_id, c2_data_create_volume, c3_data_get_volume,
                                 c4_data_create_network, c5_data_create_subnet, c6_data_create_port,
                                 c7_data_create_flavor, c8_data_list_image, c9_data_create_vm, c10_data_get_vm]
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
        data = inst_req_data
        InstVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        self.assert_job_result(self.job_id, 100, "Instantiate Vnf success.")
