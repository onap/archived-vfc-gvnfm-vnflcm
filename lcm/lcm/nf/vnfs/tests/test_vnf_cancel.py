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

from lcm.pub.database.models import NfInstModel
from lcm.pub.utils.timeutil import now_time


class TestNFTerminate(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_delete_vnf_identifier(self):
        NfInstModel.objects.create(nfinstid='1111', mnfinstid='1111', nf_name='2222',
                                   package_id='todo', vnfm_inst_id='todo', version='', vendor='',
                                   producttype='', netype='', vnfd_model='',
                                   instantiationState='VNF_INSTANTIATED', nf_desc='', vnfdid='',
                                   vnfSoftwareVersion='', vnfConfigurableProperties='todo',
                                   localizationLanguage='EN_US', create_time=now_time())
        response = self.client.delete("/openoapi/vnflcm/v1/vnf_instances/1111")
        self.failUnlessEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_vnf_identifier_when_vnf_not_exist(self):
        response = self.client.delete("/openoapi/vnflcm/v1/vnf_instances/1111")
        self.failUnlessEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("VnfInst(1111) does not exist", response.data["error"])

    def test_delete_vnf_identifier_when_instantiationState_check_failed(self):
        NfInstModel.objects.create(nfinstid='1111', mnfinstid='1111', nf_name='2222',
                                   package_id='todo', vnfm_inst_id='todo', version='', vendor='',
                                   producttype='', netype='', vnfd_model='',
                                   instantiationState='NOT_INSTANTIATED', nf_desc='', vnfdid='',
                                   vnfSoftwareVersion='', vnfConfigurableProperties='todo',
                                   localizationLanguage='EN_US', create_time=now_time())
        response = self.client.delete("/openoapi/vnflcm/v1/vnf_instances/1111")
        self.failUnlessEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("No instantiated vnf", response.data["error"])
