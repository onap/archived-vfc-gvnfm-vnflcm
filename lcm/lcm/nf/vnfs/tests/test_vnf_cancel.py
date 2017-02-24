# # Copyright 2017 ZTE Corporation.
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #         http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.
import uuid

import mock
from django.test import TestCase, Client
from rest_framework import status

from lcm.nf.vnfs.vnf_cancel.term_vnf import TermVnf
from lcm.pub.database.models import NfInstModel, JobStatusModel, VmInstModel, NetworkInstModel, SubNetworkInstModel, \
    PortInstModel, NfvoRegInfoModel
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time


class TestNFTerminate(TestCase):
    def setUp(self):
        self.client = Client()
        VmInstModel.objects.create(vmid="1", vimid="1", resouceid="11", insttype=0, instid="1111", vmname="test_01",
                                   is_predefined=1, operationalstate=1)
        VmInstModel.objects.create(vmid="2", vimid="2", resouceid="22", insttype=0, instid="1111",
                                   is_predefined=1, vmname="test_02", operationalstate=1)
        NetworkInstModel.objects.create(networkid='1', vimid='1', resouceid='1', name='pnet_network',
                                        is_predefined=1, tenant='admin', insttype=0, instid='1111')
        SubNetworkInstModel.objects.create(subnetworkid='1', vimid='1', resouceid='1', networkid='1',
                                           is_predefined=1, name='sub_pnet', tenant='admin', insttype=0, instid='1111')
        PortInstModel.objects.create(portid='1', networkid='1', subnetworkid='1', vimid='1', resouceid='1',
                                     is_predefined=1, name='aaa_pnet_cp', tenant='admin', insttype=0, instid='1111')

    def tearDown(self):
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

    def test_delete_vnf_identifier(self):
        NfInstModel.objects.create(nfinstid='1111', nf_name='2222', package_id='todo', version='', vendor='',
                                   netype='', vnfd_model='', status='VNF_INSTANTIATED', nf_desc='', vnfdid='',
                                   vnfSoftwareVersion='', vnfConfigurableProperties='todo',
                                   localizationLanguage='EN_US', create_time=now_time())
        response = self.client.delete("/openoapi/vnflcm/v1/vnf_instances/1111")
        self.failUnlessEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(None, response.data)

    def test_delete_vnf_identifier_when_vnf_not_exist(self):
        response = self.client.delete("/openoapi/vnflcm/v1/vnf_instances/1111")
        self.failUnlessEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("VnfInst(1111) does not exist", response.data["error"])

    def test_delete_vnf_identifier_when_status_check_failed(self):
        NfInstModel.objects.create(nfinstid='1111', nf_name='2222', package_id='todo', version='', vendor='',
                                   netype='', vnfd_model='', status='NOT_INSTANTIATED', nf_desc='', vnfdid='',
                                   vnfSoftwareVersion='', vnfConfigurableProperties='todo',
                                   localizationLanguage='EN_US', create_time=now_time())
        response = self.client.delete("/openoapi/vnflcm/v1/vnf_instances/1111")
        self.failUnlessEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual("Don't allow to delete vnf(status:[NOT_INSTANTIATED])", response.data["error"])

#     @mock.patch.object(TermVnf, 'run')
#     def test_terminate_vnf(self, mock_run):
#         mock_run.re.return_value = None
#         response = self.client.post("/openoapi/vnflcm/v1/vnf_instances/12/terminate", data={}, format='json')
#         self.failUnlessEqual(status.HTTP_202_ACCEPTED, response.status_code)
#
#     def test_terminate_vnf_when_inst_id_not_exist(self):
#         data = {"terminationType": "GRACEFUL",
#                 "gracefulTerminationTimeout": 120}
#         self.nf_inst_id = str(uuid.uuid4())
#         self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
#         JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
#         TermVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
#         self.assert_job_result(self.job_id, 255, "VnfInst(%s) does not exist" % self.nf_inst_id)
#
#     def test_instantiate_vnf_when_get_nfvo_config_failed(self):
#         NfInstModel.objects.create(nfinstid='1111', mnfinstid='1111', nf_name='2222',
#                                    package_id='todo', vnfm_inst_id='todo', version='', vendor='',
#                                    producttype='', netype='', vnfd_model='',
#                                    instantiationState='VNF_INSTANTIATED', nf_desc='', vnfdid='',
#                                    vnfSoftwareVersion='', vnfConfigurableProperties='todo',
#                                    localizationLanguage='EN_US', create_time=now_time())
#         data = {"terminationType": "FORCEFUL",
#                 "gracefulTerminationTimeout": 120}
#         self.nf_inst_id = '1111'
#         self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
#         JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
#         TermVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
#         self.assert_job_result(self.job_id, 255, "Nfvo was not registered")
#
#     def test_terminate_vnf_success(self):
#         NfInstModel.objects.create(nfinstid='1111', mnfinstid='1111', nf_name='2222',
#                                    package_id='todo', vnfm_inst_id='todo', version='', vendor='',
#                                    producttype='', netype='', vnfd_model='',
#                                    instantiationState='VNF_INSTANTIATED', nf_desc='', vnfdid='',
#                                    vnfSoftwareVersion='', vnfConfigurableProperties='todo',
#                                    localizationLanguage='EN_US', create_time=now_time())
#         NfvoRegInfoModel.objects.create(nfvoid='nfvo111', vnfminstid='vnfm111', apiurl='http://10.74.44.11',
#                                         nfvouser='root', nfvopassword='root123')
#         data = {"terminationType": "FORCEFUL",
#                 "gracefulTerminationTimeout": 120}
#         self.nf_inst_id = '1111'
#         self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
#         JobUtil.add_job_status(self.job_id, 0, "INST_VNF_READY")
#         TermVnf(data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
#         self.assert_job_result(self.job_id, 100, "Terminate Vnf success.")
