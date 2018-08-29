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
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from lcm.nf.biz.heal_vnf import HealVnf
from lcm.nf.const import c1_data_get_tenant_id_1, c9_data_create_vm, c10_data_get_vm, vnfd_model_dict
from lcm.pub.database.models import NfInstModel, JobStatusModel, VmInstModel
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.vimapi import api


class TestNFInstantiate(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.grant_result = {
            "vimid": 'vimid_1',
            "tenant": 'tenantname_1',
        }
        self.getvmResult = {
            "status": "ACTIVE",
            "id": "11",
        }

    def tearDown(self):
        pass

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(jobid=job_id,
                                             progress=job_progress,
                                             descp=job_detail)
        self.assertEqual(1, len(jobs))

    def test_heal_vnf_not_found(self):
        req_data = {}
        response = self.client.post("/api/vnflcm/v1/vnf_instances/12/heal", data=req_data, format='json')
        self.failUnlessEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_heal_vnf_conflict(self):
        req_data = {}
        NfInstModel(nfinstid='12', nf_name='VNF1', status='NOT_INSTANTIATED').save()
        response = self.client.post("/api/vnflcm/v1/vnf_instances/12/heal", data=req_data, format='json')
        self.failUnlessEqual(status.HTTP_409_CONFLICT, response.status_code)
        NfInstModel(nfinstid='12', nf_name='VNF1', status='NOT_INSTANTIATED').delete()

    @mock.patch.object(HealVnf, 'run')
    def test_heal_vnf_success(self, mock_run):
        req_data = {}
        NfInstModel(nfinstid='12', nf_name='VNF1', status='INSTANTIATED').save()
        response = self.client.post("/api/vnflcm/v1/vnf_instances/12/heal", data=req_data, format='json')
        mock_run.re.return_value = None
        self.failUnlessEqual(status.HTTP_202_ACCEPTED, response.status_code)
        NfInstModel(nfinstid='12', nf_name='VNF1', status='INSTANTIATED').delete()

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_heal_vnf_success_reboot(self, mock_call, mock_call_req):
        vim_cache = {}
        res_cache = {}

        NfInstModel.objects.create(nfinstid='1111',
                                   nf_name='2222',
                                   vnfminstid='1',
                                   package_id='todo',
                                   version='',
                                   vendor='',
                                   netype='',
                                   vnfd_model=json.dumps(vnfd_model_dict),
                                   status='INSTANTIATED',
                                   nf_desc='',
                                   vnfdid='',
                                   vnfSoftwareVersion='',
                                   vnfConfigurableProperties='todo',
                                   localizationLanguage='EN_US',
                                   create_time=now_time(),
                                   resInfo=json.dumps(res_cache),
                                   vimInfo=json.dumps(vim_cache))

        VmInstModel.objects.create(vmid="1",
                                   vimid="vimid_1",
                                   resourceid="11",
                                   insttype=0,
                                   instid="1111",
                                   vmname="vduinstname",
                                   is_predefined=1,
                                   tenant="tenantname_1",
                                   operationalstate=1)
        t1_apply_grant_result = [0, json.JSONEncoder().encode(self.grant_result), '200']
        t2_lcm_notify_result = [0, json.JSONEncoder().encode(''), '200']
        t3_action_get_vm = [0, json.JSONEncoder().encode(self.getvmResult), '202']
        t4_action_vm_start_reboot = [0, json.JSONEncoder().encode(''), '202']
        mock_call_req.side_effect = [t1_apply_grant_result, t2_lcm_notify_result, t3_action_get_vm, t4_action_vm_start_reboot]
        mock_call.side_effect = [self.getvmResult, None]
        req_data = {
            "cause": "Error",
            "additionalParams": {
                "action": "vmReset",
                "affectedvm": {
                    "vmid": "1",
                    "vduid": "vdu1Id",
                    "vmname": "vduinstname"
                }
            }
        }
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'HEAL', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "HEAL_VNF_READY")
        HealVnf(req_data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        self.assert_job_result(self.job_id, 100, "Heal Vnf success.")

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_heal_vnf_success_start(self, mock_call, mock_call_req):
        vim_cache = {}
        res_cache = {"volume": {}, "flavor": {}, "port": {}}
        res_cache["volume"]["volume_storage1"] = "vol1"
        res_cache["flavor"]["vdu1Id"] = "flavor1"
        res_cache["port"]["cpId1"] = "port1"

        NfInstModel.objects.create(nfinstid='1111',
                                   nf_name='2222',
                                   vnfminstid='1',
                                   package_id='todo',
                                   version='',
                                   vendor='',
                                   netype='',
                                   vnfd_model=json.dumps(vnfd_model_dict),
                                   status='INSTANTIATED',
                                   nf_desc='',
                                   vnfdid='',
                                   vnfSoftwareVersion='',
                                   vnfConfigurableProperties='todo',
                                   localizationLanguage='EN_US',
                                   resInfo=json.dumps(res_cache),
                                   vimInfo=json.dumps(vim_cache),
                                   create_time=now_time())

        t1_apply_grant_result = [0, json.JSONEncoder().encode(self.grant_result), '200']
        t2_lcm_notify_result = [0, json.JSONEncoder().encode(''), '200']
        t3_action_vm_start_create = [0, json.JSONEncoder().encode(''), '202']
        mock_call_req.side_effect = [t1_apply_grant_result, t2_lcm_notify_result, t3_action_vm_start_create]
        mock_call.side_effect = [c1_data_get_tenant_id_1, c9_data_create_vm, c10_data_get_vm]
        req_data = {
            "cause": "Error",
            "additionalParams": {
                "action": "vmCreate",
                "affectedvm": {
                    "vmid": "1",
                    "vduid": "vdu1Id",
                    "vmname": "vduinstname"
                }
            }
        }
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'HEAL', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "HEAL_VNF_READY")
        HealVnf(req_data, nf_inst_id=self.nf_inst_id, job_id=self.job_id).run()
        self.assert_job_result(self.job_id, 100, "Heal Vnf success.")
