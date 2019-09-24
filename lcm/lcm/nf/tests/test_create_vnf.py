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

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .const import vnfpackage_info
from lcm.pub.database.models import NfInstModel
from lcm.pub.database.models import JobStatusModel
from lcm.pub.utils import restcall
from lcm.pub.utils.timeutil import now_time
from lcm.pub.exceptions import NFLCMException
from lcm.nf.biz.create_vnf import CreateVnf


class TestNFInstantiate(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.grant_result = {
            "vimid": 'vimid_1',
            "tenant": 'tenantname_1'
        }

    def tearDown(self):
        pass

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(
            jobid=job_id,
            progress=job_progress,
            descp=job_detail
        )
        self.assertEqual(1, len(jobs))

    def test_create_vnf_identifier_when_vnf_is_exist(self):
        NfInstModel.objects.create(
            nfinstid='1111',
            nf_name='vFW_01',
            package_id='222',
            version='',
            vendor='',
            netype='',
            vnfd_model='',
            status='NOT_INSTANTIATED',
            nf_desc='vFW in Nanjing TIC Edge',
            vnfdid='111',
            create_time=now_time()
        )
        data = {
            "vnfdId": "111",
            "vnfInstanceName": "vFW_01",
            "vnfInstanceDescription": "vFW in Nanjing TIC Edge"
        }
        response = self.client.post(
            "/api/vnflcm/v1/vnf_instances",
            data=data,
            format='json'
        )
        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code
        )
        context = json.loads(response.content)
        self.assertEqual({
            'detail': 'VNF is already exist.',
            'status': 500
        }, context)

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(uuid, 'uuid4')
    def test_create_vnf_identifier(self, mock_uuid4, mock_call_req):
        r2_get_vnfpackage_from_catalog = [
            0,
            json.JSONEncoder().encode(vnfpackage_info),
            '200'
        ]
        mock_call_req.return_value = r2_get_vnfpackage_from_catalog
        mock_uuid4.return_value = "1"
        data = {
            "vnfdId": "111",
            "vnfInstanceName": "vFW_01",
            "vnfInstanceDescription": "vFW in Nanjing TIC Edge"
        }
        response = self.client.post(
            "/api/vnflcm/v1/vnf_instances",
            data=data,
            format='json'
        )
        expect_data = {
            "id": "1",
            "vnfProvider": "huawei",
            'vnfInstanceDescription': 'vFW in Nanjing TIC Edge',
            'vnfInstanceName': 'vFW_01',
            "vnfdVersion": "1.0",
            "vnfPkgId": "111",
            "instantiationState": "NOT_INSTANTIATED",
            'vnfSoftwareVersion': '1.0',
            'vnfdId': '111'
        }
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(expect_data, response.data)

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(uuid, 'uuid4')
    def test_create_vnf_inner_error(self, mock_uuid4, mock_call_req):
        mock_call_req.side_effect = NFLCMException('Boom!')
        mock_uuid4.return_value = "1"
        data = {
            "vnfdId": "111",
            "vnfInstanceName": "vFW_01",
            "vnfInstanceDescription": "vFW in Nanjing TIC Edge"
        }
        response = self.client.post(
            "/api/vnflcm/v1/vnf_instances",
            data=data,
            format='json'
        )
        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)

    def test_create_vnf_bad_req(self):
        data = {
            "vnfInstanceName": "vFW_01",
            "vnfInstanceDescription": "vFW in Nanjing TIC Edge"
        }
        response = self.client.post(
            "/api/vnflcm/v1/vnf_instances",
            data=data,
            format='json'
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock.patch.object(CreateVnf, 'do_biz')
    def test_create_vnf_bad_response(self, moc_CreateVnf_do_biz):
        moc_CreateVnf_do_biz.return_value = {
            # "id": "1",
            "vnfProvider": "huawei",
            "vnfdVersion": "1.0",
            "vnfPkgId": "111",
            "instantiationState": "NOT_INSTANTIATED"
        }
        data = {
            "vnfdId": "111",
            "vnfInstanceName": "vFW_01",
            "vnfInstanceDescription": "vFW in Nanjing TIC Edge"
        }
        response = self.client.post(
            "/api/vnflcm/v1/vnf_instances",
            data=data,
            format='json'
        )
        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
