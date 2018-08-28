# Copyright (C) 2018 Verizon. All Rights Reserved.
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

import json

import mock
from django.test import TestCase, Client
from rest_framework import status

from lcm.nf.biz.operate_vnf import OperateVnf
from lcm.pub.database.models import NfInstModel, JobStatusModel, VmInstModel
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.vimapi import api


class TestNFOperate(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        VmInstModel.objects.all().delete()

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(jobid=job_id,
                                             progress=job_progress,
                                             descp=job_detail)
        self.assertEqual(1, len(jobs))

    def test_operate_vnf_not_found(self):
        req_data = {
            "changeStateTo": "STARTED"
        }
        response = self.client.post("/api/vnflcm/v1/vnf_instances/12/operate", data=req_data, format='json')
        self.failUnlessEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_operate_vnf_conflict(self):
        req_data = {
            "changeStateTo": "STARTED"
        }
        NfInstModel(nfinstid='12', nf_name='VNF1', status='NOT_INSTANTIATED').save()
        response = self.client.post("/api/vnflcm/v1/vnf_instances/12/operate", data=req_data, format='json')
        self.failUnlessEqual(status.HTTP_409_CONFLICT, response.status_code)
        NfInstModel(nfinstid='12', nf_name='VNF1', status='NOT_INSTANTIATED').delete()

    @mock.patch.object(OperateVnf, 'run')
    def test_operate_vnf_success(self, mock_run):
        req_data = {
            "changeStateTo": "STARTED"
        }
        NfInstModel(nfinstid='12', nf_name='VNF1', status='INSTANTIATED').save()
        response = self.client.post("/api/vnflcm/v1/vnf_instances/12/operate", data=req_data, format='json')
        mock_run.re.return_value = None
        self.failUnlessEqual(status.HTTP_202_ACCEPTED, response.status_code)
        NfInstModel(nfinstid='12', nf_name='VNF1', status='INSTANTIATED').delete()

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_operate_vnf_success_start(self, mock_call, mock_call_req):
        NfInstModel.objects.create(nfinstid='1111',
                                   nf_name='2222',
                                   vnfminstid='1',
                                   package_id='todo',
                                   version='',
                                   vendor='',
                                   netype='',
                                   vnfd_model='',
                                   status='INSTANTIATED',
                                   nf_desc='',
                                   vnfdid='',
                                   vnfSoftwareVersion='',
                                   vnfConfigurableProperties='todo',
                                   localizationLanguage='EN_US',
                                   create_time=now_time())

        VmInstModel.objects.create(vmid="1",
                                   vimid="1",
                                   resouceid="11",
                                   insttype=0,
                                   instid="1111",
                                   vmname="test_01",
                                   is_predefined=1,
                                   operationalstate=1)
        t1_apply_grant_result = [0, json.JSONEncoder().encode(''), '200']
        t2_lcm_notify_result = [0, json.JSONEncoder().encode(''), '200']
        t3_action_vm_start_result = [0, json.JSONEncoder().encode(''), '202']
        mock_call_req.side_effect = [t1_apply_grant_result, t2_lcm_notify_result, t3_action_vm_start_result]
        mock_call.return_value = None
        req_data = {
            "changeStateTo": "STARTED"
        }
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'OPERATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "OPERATE_VNF_READY")
        OperateVnf(req_data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        vm = VmInstModel.objects.filter(vmid="1", vimid="1", resouceid="11")
        self.assertEqual("ACTIVE", vm[0].operationalstate)
        self.assert_job_result(self.job_id, 100, "Operate Vnf success.")

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_operate_vnf_success_stop(self, mock_call, mock_call_req):
        NfInstModel.objects.create(nfinstid='1111',
                                   nf_name='2222',
                                   vnfminstid='1',
                                   package_id='todo',
                                   version='',
                                   vendor='',
                                   netype='',
                                   vnfd_model='',
                                   status='INSTANTIATED',
                                   nf_desc='',
                                   vnfdid='',
                                   vnfSoftwareVersion='',
                                   vnfConfigurableProperties='todo',
                                   localizationLanguage='EN_US',
                                   create_time=now_time())

        VmInstModel.objects.create(vmid="1",
                                   vimid="1",
                                   resouceid="11",
                                   insttype=0,
                                   instid="1111",
                                   vmname="test_01",
                                   is_predefined=1,
                                   operationalstate=1)
        t1_apply_grant_result = [0, json.JSONEncoder().encode(''), '200']
        t2_lcm_notify_result = [0, json.JSONEncoder().encode(''), '200']
        t3_action_vm_stop_result = [0, json.JSONEncoder().encode(''), '202']
        mock_call_req.side_effect = [t1_apply_grant_result, t2_lcm_notify_result, t3_action_vm_stop_result]
        mock_call.return_value = None
        req_data = {
            "changeStateTo": "STOPPED"
        }
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'OPERATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "OPERATE_VNF_READY")
        OperateVnf(req_data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        vm = VmInstModel.objects.filter(vmid="1", vimid="1", resouceid="11")
        self.assertEqual("INACTIVE", vm[0].operationalstate)
        self.assert_job_result(self.job_id, 100, "Operate Vnf success.")

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_operate_vnf_success_stop_graceful(self, mock_call, mock_call_req):
        NfInstModel.objects.create(nfinstid='1111',
                                   nf_name='2222',
                                   vnfminstid='1',
                                   package_id='todo',
                                   version='',
                                   vendor='',
                                   netype='',
                                   vnfd_model='',
                                   status='INSTANTIATED',
                                   nf_desc='',
                                   vnfdid='',
                                   vnfSoftwareVersion='',
                                   vnfConfigurableProperties='todo',
                                   localizationLanguage='EN_US',
                                   create_time=now_time())

        VmInstModel.objects.create(vmid="1",
                                   vimid="1",
                                   resouceid="11",
                                   insttype=0,
                                   instid="1111",
                                   vmname="test_01",
                                   is_predefined=1,
                                   operationalstate=1)
        t1_apply_grant_result = [0, json.JSONEncoder().encode(''), '200']
        t2_lcm_notify_result = [0, json.JSONEncoder().encode(''), '200']
        t3_action_vm_stop_result = [0, json.JSONEncoder().encode(''), '202']
        mock_call_req.side_effect = [t1_apply_grant_result, t2_lcm_notify_result, t3_action_vm_stop_result]
        mock_call.return_value = None
        req_data = {
            "changeStateTo": "STOPPED",
            "stopType": "GRACEFUL",
            "gracefulStopTimeout": 2
        }
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'OPERATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "OPERATE_VNF_READY")
        OperateVnf(req_data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        vm = VmInstModel.objects.filter(vmid="1", vimid="1", resouceid="11")
        self.assertEqual("INACTIVE", vm[0].operationalstate)
        self.assert_job_result(self.job_id, 100, "Operate Vnf success.")

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_operate_vnf_success_stop_forceful(self, mock_call, mock_call_req):
        NfInstModel.objects.create(nfinstid='1111',
                                   nf_name='2222',
                                   vnfminstid='1',
                                   package_id='todo',
                                   version='',
                                   vendor='',
                                   netype='',
                                   vnfd_model='',
                                   status='INSTANTIATED',
                                   nf_desc='',
                                   vnfdid='',
                                   vnfSoftwareVersion='',
                                   vnfConfigurableProperties='todo',
                                   localizationLanguage='EN_US',
                                   create_time=now_time())

        VmInstModel.objects.create(vmid="1",
                                   vimid="1",
                                   resouceid="11",
                                   insttype=0,
                                   instid="1111",
                                   vmname="test_01",
                                   is_predefined=1,
                                   operationalstate=1)
        t1_apply_grant_result = [0, json.JSONEncoder().encode(''), '200']
        t2_lcm_notify_result = [0, json.JSONEncoder().encode(''), '200']
        t3_action_vm_stop_result = [0, json.JSONEncoder().encode(''), '202']
        mock_call_req.side_effect = [t1_apply_grant_result, t2_lcm_notify_result, t3_action_vm_stop_result]
        mock_call.return_value = None
        req_data = {
            "changeStateTo": "STOPPED",
            "stopType": "FORCEFUL",
        }
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'OPERATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "OPERATE_VNF_READY")
        OperateVnf(req_data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        vm = VmInstModel.objects.filter(vmid="1", vimid="1", resouceid="11")
        self.assertEqual("INACTIVE", vm[0].operationalstate)
        self.assert_job_result(self.job_id, 100, "Operate Vnf success.")
