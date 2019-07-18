# Copyright (C) 2019 ZTE. All Rights Reserved.
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
from . import const
from lcm.pub.database.models import NfInstModel, JobStatusModel, StorageInstModel, NetworkInstModel, \
    SubNetworkInstModel, PortInstModel, FlavourInstModel, VmInstModel, VNFCInstModel
from lcm.pub.utils import restcall
from lcm.pub.vimapi import api
from lcm.pub.utils.jobutil import JobUtil
from lcm.nf.biz.scale_vnf_to_level import ScaleVnfToLevel


class TestNfScaleToLevel(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.req_data = {
            "instantiationLevelId": "instantiation_level_2",
            "scaleInfo": []
        }
        NfInstModel(nfinstid='98765',
                    nf_name='VNF1',
                    nf_desc="VNF DESC",
                    vnfdid="1",
                    netype="XGW",
                    vendor="ZTE",
                    vnfSoftwareVersion="V1",
                    version="V1",
                    package_id="2",
                    status='NOT_INSTANTIATED').save()

    def tearDown(self):
        NfInstModel.objects.filter(nfinstid='98765').delete()

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(
            jobid=job_id,
            progress=job_progress,
            descp=job_detail
        )
        self.assertEqual(1, len(jobs))

    def test_scale_vnf_to_level_not_found(self):
        url = "/api/vnflcm/v1/vnf_instances/12/scale_to_level"
        response = self.client.post(url,
                                    data=self.req_data,
                                    format='json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_scale_vnf_conflict(self):
        url = "/api/vnflcm/v1/vnf_instances/98765/scale_to_level"
        response = self.client.post(url,
                                    data=self.req_data,
                                    format='json')
        self.assertEqual(status.HTTP_409_CONFLICT, response.status_code)

    def test_scale_to_level_badreq(self):
        NfInstModel(nfinstid='678',
                    nf_name='VNF1',
                    nf_desc="VNF DESC",
                    vnfdid="1",
                    netype="XGW",
                    vendor="ZTE",
                    vnfSoftwareVersion="V1",
                    version="V1",
                    package_id="2",
                    status='INSTANTIATED').save()
        url = "/api/vnflcm/v1/vnf_instances/678/scale_to_level"
        response = self.client.post(url,
                                    data={},
                                    format='json')
        NfInstModel.objects.filter(nfinstid='678').delete()
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_scale_out_vnf_success(self, mock_call, mock_call_req):
        self.nf_inst_id = '6789'
        res_cache = {"volume": {}, "flavor": {}, "port": {}}
        res_cache["port"]["ext_cp"] = "port1"
        NfInstModel(nfinstid=self.nf_inst_id,
                    nf_name='VNF1',
                    nf_desc="VNF DESC",
                    vnfdid="1",
                    netype="XGW",
                    vendor="ZTE",
                    vnfSoftwareVersion="V1",
                    version="V1",
                    package_id="2",
                    status='INSTANTIATED',
                    vnfd_model=json.dumps(const.vnfd_for_scale),
                    vimInfo=json.dumps({}),
                    resInfo=json.dumps(res_cache)).save()
        StorageInstModel.objects.create(
            storageid="1",
            vimid="1",
            resourceid="11",
            insttype=0,
            instid=self.nf_inst_id,
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
            instid=self.nf_inst_id
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
            instid=self.nf_inst_id
        )
        PortInstModel.objects.create(
            portid='1',
            networkid='1',
            subnetworkid='1',
            vimid='1',
            resourceid='1',
            is_predefined=1,
            name='ext_cp',
            tenant='admin',
            insttype=0,
            instid=self.nf_inst_id
        )
        FlavourInstModel.objects.create(
            flavourid="1",
            vimid="1",
            resourceid="11",
            instid=self.nf_inst_id,
            is_predefined=1,
            name="Flavor_sunshine"
        )
        VmInstModel.objects.create(
            vmid="1",
            vimid="1",
            resourceid="11",
            insttype=0,
            instid=self.nf_inst_id,
            vmname="test_01",
            is_predefined=1,
            operationalstate=1
        )
        r1_apply_grant_result = [
            0,
            json.JSONEncoder().encode(const.instantiate_grant_result),
            '200'
        ]
        mock_call_req.side_effect = [
            r1_apply_grant_result,
        ]
        mock_call.side_effect = [
            const.c1_data_get_tenant_id,
            const.c7_data_create_flavor,
            const.c8_data_list_image,
            const.c9_data_create_vm,
            const.c10_data_get_vm
        ]

        self.job_id = JobUtil.create_job('NF', 'SCALE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "VNF_SCALE_READY", )

        ScaleVnfToLevel(
            {"instantiationLevelId": "instantiation_level_2"},
            nf_inst_id=self.nf_inst_id,
            job_id=self.job_id
        ).run()

        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).delete()
        print([job.descp for job in JobStatusModel.objects.filter(jobid=self.job_id)])
        self.assert_job_result(
            self.job_id,
            100,
            'Scale Vnf success.'
        )

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_scale_to_inlevel_vnf_success(self, mock_call, mock_call_req):
        self.nf_inst_id = '6789'
        res_cache = {"volume": {}, "flavor": {}, "port": {}}
        res_cache["port"]["ext_cp"] = "port1"
        NfInstModel(nfinstid=self.nf_inst_id,
                    nf_name='VNF1',
                    nf_desc="VNF DESC",
                    vnfdid="1",
                    netype="XGW",
                    vendor="ZTE",
                    vnfSoftwareVersion="V1",
                    version="V1",
                    package_id="2",
                    status='INSTANTIATED',
                    vnfd_model=json.dumps(const.vnfd_for_scale),
                    vimInfo=json.dumps({}),
                    resInfo=json.dumps(res_cache)).save()
        StorageInstModel.objects.create(
            storageid="1",
            vimid="1",
            resourceid="11",
            insttype=0,
            instid=self.nf_inst_id,
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
            instid=self.nf_inst_id
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
            instid=self.nf_inst_id
        )
        PortInstModel.objects.create(
            portid='1',
            networkid='1',
            subnetworkid='1',
            vimid='1',
            resourceid='1',
            is_predefined=1,
            name='ext_cp',
            tenant='admin',
            insttype=0,
            instid=self.nf_inst_id
        )
        FlavourInstModel.objects.create(
            flavourid="1",
            vimid="1",
            resourceid="11",
            instid=self.nf_inst_id,
            is_predefined=1,
            name="Flavor_sunshine"
        )
        VmInstModel.objects.create(
            vmid="1",
            vimid="1",
            resourceid="11",
            insttype=0,
            instid=self.nf_inst_id,
            vmname="test_01",
            is_predefined=1,
            operationalstate=1
        )
        VmInstModel.objects.create(
            vmid="2",
            vimid="1",
            resourceid="22",
            insttype=0,
            instid=self.nf_inst_id,
            vmname="test_02",
            is_predefined=1,
            operationalstate=1
        )
        VNFCInstModel.objects.create(
            vnfcinstanceid="1",
            instid=self.nf_inst_id,
            vmid="1"
        )
        VNFCInstModel.objects.create(
            vnfcinstanceid="2",
            instid=self.nf_inst_id,
            vmid="2"
        )
        r1_apply_grant_result = [
            0,
            json.JSONEncoder().encode(const.instantiate_grant_result),
            '200'
        ]
        mock_call_req.side_effect = [
            r1_apply_grant_result,
        ]
        mock_call.side_effect = [
            const.c1_data_get_tenant_id,
            const.c7_data_create_flavor,
            const.c8_data_list_image,
            const.c9_data_create_vm,
            const.c10_data_get_vm
        ]

        self.job_id = JobUtil.create_job('NF', 'SCALE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "VNF_SCALE_READY", )

        ScaleVnfToLevel(
            {"scaleInfo": {"aspectId": "sunshine_aspect",
                           "scaleLevel": 0}},
            nf_inst_id=self.nf_inst_id,
            job_id=self.job_id
        ).run()

        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).delete()
        print([job.descp for job in JobStatusModel.objects.filter(jobid=self.job_id)])
        self.assert_job_result(
            self.job_id,
            100,
            'Scale Vnf success.'
        )
