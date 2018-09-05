# Copyright (C) 2018 Verizon. All Rights Reserved
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

from django.test import TestCase, Client
from rest_framework import status

from lcm.pub.database.models import VNFLcmOpOccModel


class TestVNFLcmOpOccs(TestCase):
    def setUp(self):
        self.client = Client()
        self.vnf_lcm_op_occ_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        VNFLcmOpOccModel.objects.all().delete()
        self.test_single_vnf_lcm_op = {
            "id": "99442b18-a5c7-11e8-998c-bf1755941f16",
            "operationState": "STARTING",
            "stateEnteredTime": "2018-07-09",
            "startTime": "2018-07-09",
            "vnfInstanceId": "cd552c9c-ab6f-11e8-b354-236c32aa91a1",
            "grantId": None,
            "operation": "SCALE",
            "isAutomaticInvocation": False,
            "operationParams": {},
            "isCancelPending": False,
            "cancelMode": None,
            "error": None,
            "resourceChanges": None,
            "changedInfo": None,
            "changedExtConnectivity": None,
            "_links": {
                "self": "demo",
                "vnfInstance": "demo"
            }
        }
        self.test_vnflcmop_with_exclude_default = [{
            "id": "99442b18-a5c7-11e8-998c-bf1755941f16",
            "operationState": "STARTING",
            "stateEnteredTime": "2018-07-09",
            "startTime": "2018-07-09",
            "vnfInstanceId": "cd552c9c-ab6f-11e8-b354-236c32aa91a1",
            "grantId": None,
            "operation": "SCALE",
            "isAutomaticInvocation": False,
            "isCancelPending": False,
            "cancelMode": None,
            "_links": {
                "self": "demo",
                "vnfInstance": "demo"
            }
        }]

        self.test_multiple_vnf_lcm_op = [{
            "id": "a6b9415c-ab99-11e8-9d37-dbb5e0378955",
            "operationState": "STARTING",
            "stateEnteredTime": "2018-07-09",
            "startTime": "2018-07-09",
            "vnfInstanceId": "cd552c9c-ab6f-11e8-b354-236c32aa91a1",
            "grantId": None,
            "operation": "INSTANTIATE",
            "isAutomaticInvocation": False,
            "operationParams": {},
            "isCancelPending": False,
            "cancelMode": None,
            "error": None,
            "resourceChanges": None,
            "changedInfo": None,
            "changedExtConnectivity": None,
            "_links": {
                "self": "demo",
                "vnfInstance": "demo"
            }
        }]
        self.test_multiple_vnf_lcm_op.append(
            self.test_single_vnf_lcm_op)

    def tearDown(self):
        pass

    def test_get_vnflcmopoccs(self):
        lcm_op_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        vnf_instance_id = "cd552c9c-ab6f-11e8-b354-236c32aa91a1"
        VNFLcmOpOccModel(id=lcm_op_id, operation_state="STARTING",
                         state_entered_time="2018-07-09", start_time="2018-07-09",
                         vnf_instance_id=vnf_instance_id,
                         grant_id=None, operation="SCALE", is_automatic_invocation=False,
                         operation_params='{}', is_cancel_pending=False, cancel_mode=None,
                         error=None, resource_changes=None, changed_ext_connectivity=None,
                         links=json.dumps({"self": "demo", "vnfInstance": "demo"})).save()
        response = self.client.get("/api/vnflcm/v1/vnf_lcm_op_occs", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([self.test_single_vnf_lcm_op], response.data)

    def test_get_vnflcmopoccs_with_id_not_exist(self):
        response = self.client.get("/api/vnflcm/v1/vnf_lcm_op_occs?id=dummy", format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        expected_data = {
            "status": 500,
            "detail": "LCM Operation Occurances do not exist"
        }
        self.assertEqual(expected_data, response.data)

    def test_get_vnflcmopoccs_with_filters(self):
        lcm_op_id = "a6b9415c-ab99-11e8-9d37-dbb5e0378955"
        vnf_instance_id = "cd552c9c-ab6f-11e8-b354-236c32aa91a1"
        VNFLcmOpOccModel(id=lcm_op_id, operation_state="STARTING",
                         state_entered_time="2018-07-09", start_time="2018-07-09",
                         vnf_instance_id=vnf_instance_id,
                         grant_id=None, operation="INSTANTIATE", is_automatic_invocation=False,
                         operation_params='{}', is_cancel_pending=False, cancel_mode=None,
                         error=None, resource_changes=None, changed_ext_connectivity=None,
                         links=json.dumps({"self": "demo", "vnfInstance": "demo"})).save()

        lcm_op_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        VNFLcmOpOccModel(id=lcm_op_id, operation_state="STARTING",
                         state_entered_time="2018-07-09", start_time="2018-07-09",
                         vnf_instance_id=vnf_instance_id,
                         grant_id=None, operation="SCALE", is_automatic_invocation=False,
                         operation_params='{}', is_cancel_pending=False, cancel_mode=None,
                         error=None, resource_changes=None, changed_ext_connectivity=None,
                         links=json.dumps({"self": "demo", "vnfInstance": "demo"})).save()
        response = self.client.get("/api/vnflcm/v1/vnf_lcm_op_occs", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_multiple_vnf_lcm_op, response.data)

        response = self.client.get("/api/vnflcm/v1/vnf_lcm_op_occs?operation=SCALE", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([self.test_single_vnf_lcm_op], response.data)

        response = self.client.get("/api/vnflcm/v1/vnf_lcm_op_occs?vnfInstanceId=%s" % vnf_instance_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_multiple_vnf_lcm_op, response.data)

    def test_get_vnflcmopoccs_with_extra_flags(self):
        lcm_op_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        vnf_instance_id = "cd552c9c-ab6f-11e8-b354-236c32aa91a1"
        VNFLcmOpOccModel(id=lcm_op_id, operation_state="STARTING",
                         state_entered_time="2018-07-09", start_time="2018-07-09",
                         vnf_instance_id=vnf_instance_id,
                         grant_id=None, operation="SCALE", is_automatic_invocation=False,
                         operation_params='{}', is_cancel_pending=False, cancel_mode=None,
                         error=None, resource_changes=None, changed_ext_connectivity=None,
                         links=json.dumps({"self": "demo", "vnfInstance": "demo"})).save()
        response = self.client.get("/api/vnflcm/v1/vnf_lcm_op_occs?exclude_default", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_vnflcmop_with_exclude_default, response.data)

    def test_get_vnflcmopocc_with_id(self):
        lcm_op_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        vnf_instance_id = "cd552c9c-ab6f-11e8-b354-236c32aa91a1"
        VNFLcmOpOccModel(id=lcm_op_id, operation_state="STARTING",
                         state_entered_time="2018-07-09", start_time="2018-07-09",
                         vnf_instance_id=vnf_instance_id,
                         grant_id=None, operation="SCALE", is_automatic_invocation=False,
                         operation_params='{}', is_cancel_pending=False, cancel_mode=None,
                         error=None, resource_changes=None, changed_ext_connectivity=None,
                         links=json.dumps({"self": "demo", "vnfInstance": "demo"})).save()
        response = self.client.get("/api/vnflcm/v1/vnf_lcm_op_occs/" + lcm_op_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_single_vnf_lcm_op, response.data)

    def test_single_vnflcmopocc_with_unknown_id(self):
        lcm_op_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        response = self.client.get("/api/vnflcm/v1/vnf_lcm_op_occs/" + lcm_op_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        expected_data = {
            "status": 500,
            "detail": "LCM Operation Occurance does not exist"
        }
        self.assertEqual(expected_data, response.data)
