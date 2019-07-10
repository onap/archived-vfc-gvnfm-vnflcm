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

import mock
from django.test import TestCase, Client
from rest_framework import status

from lcm.pub.database.models import NfInstModel
from lcm.pub.database.models import JobStatusModel
from lcm.pub.database.models import VmInstModel
from lcm.pub.database.models import NetworkInstModel
from lcm.pub.database.models import SubNetworkInstModel
from lcm.pub.database.models import PortInstModel
from lcm.pub.database.models import FlavourInstModel
from lcm.pub.database.models import StorageInstModel
from lcm.pub.database.models import NfvoRegInfoModel
from lcm.pub.utils.timeutil import now_time
from lcm.nf.biz.delete_vnf import DeleteVnf
from lcm.pub.exceptions import NFLCMException


class TestNFTerminate(TestCase):
    def setUp(self):
        self.client = Client()
        StorageInstModel.objects.create(
            storageid="1",
            vimid="1",
            resourceid="11",
            insttype=0,
            instid="1111",
            is_predefined=1
        )
        NetworkInstModel.objects.create(
            networkid='1',
            vimid='1',
            resourceid='1',
            name='pnet_network',
            is_predefined=1,
            tenant='admin',
            insttype=0,
            instid='1111'
        )
        SubNetworkInstModel.objects.create(
            subnetworkid='1',
            vimid='1',
            resourceid='1',
            networkid='1',
            is_predefined=1,
            name='sub_pnet',
            tenant='admin',
            insttype=0,
            instid='1111'
        )
        PortInstModel.objects.create(
            portid='1',
            networkid='1',
            subnetworkid='1',
            vimid='1',
            resourceid='1',
            is_predefined=1,
            name='aaa_pnet_cp',
            tenant='admin',
            insttype=0,
            instid='1111'
        )
        FlavourInstModel.objects.create(
            flavourid="1",
            vimid="1",
            resourceid="11",
            instid="1111",
            is_predefined=1
        )
        VmInstModel.objects.create(
            vmid="1",
            vimid="1",
            resourceid="11",
            insttype=0,
            instid="1111",
            vmname="test_01",
            is_predefined=1,
            operationalstate=1
        )
        NfvoRegInfoModel.objects.create(
            nfvoid='1111',
            vnfminstid='11111',
            apiurl='1'
        )

    def tearDown(self):
        VmInstModel.objects.all().delete()
        NetworkInstModel.objects.all().delete()
        SubNetworkInstModel.objects.all().delete()
        PortInstModel.objects.all().delete()

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(
            jobid=job_id,
            progress=job_progress,
            descp=job_detail
        )
        self.assertEqual(1, len(jobs))

    def test_delete_vnf_identifier(self):
        NfInstModel.objects.create(
            nfinstid='1111',
            nf_name='2222',
            package_id='todo',
            version='',
            vendor='',
            netype='',
            vnfd_model='',
            status='NOT_INSTANTIATED',
            nf_desc='',
            vnfdid='',
            vnfSoftwareVersion='',
            vnfConfigurableProperties='todo',
            localizationLanguage='EN_US',
            create_time=now_time()
        )
        response = self.client.delete("/api/vnflcm/v1/vnf_instances/1111")
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(None, response.data)

    def test_delete_vnf_identifier_when_vnf_not_exist(self):
        response = self.client.delete("/api/vnflcm/v1/vnf_instances/1111")
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    @mock.patch.object(DeleteVnf, 'do_biz')
    def test_delete_vnf_inner_error(self, mock_DeleteVnf_do_biz):
        mock_DeleteVnf_do_biz.side_effect = NFLCMException('Boom!')
        response = self.client.delete("/api/vnflcm/v1/vnf_instances/1234")
        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
