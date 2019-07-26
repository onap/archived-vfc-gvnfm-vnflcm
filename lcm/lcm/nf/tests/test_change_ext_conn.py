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

from lcm.pub.database.models import NfInstModel, JobStatusModel, StorageInstModel, NetworkInstModel, \
    SubNetworkInstModel, PortInstModel, FlavourInstModel, VmInstModel, VNFCInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils import restcall
from lcm.pub.vimapi import api
from lcm.pub.utils.jobutil import JobUtil
from lcm.nf.biz.change_ext_conn import ChangeExtConn
from . import const


class TestChangeExtConn(TestCase):
    def setUp(self):
        self.client = APIClient()
        NfInstModel(nfinstid='12345',
                    nf_name='VNF1',
                    nf_desc="VNF DESC",
                    vnfdid="1",
                    netype="XGW",
                    vendor="ZTE",
                    vnfSoftwareVersion="V1",
                    version="V1",
                    package_id="2",
                    status='NOT_INSTANTIATED').save()
        NfInstModel(nfinstid='123',
                    nf_name='VNF1',
                    nf_desc="VNF DESC",
                    vnfdid="1",
                    netype="XGW",
                    vendor="ZTE",
                    vnfSoftwareVersion="V1",
                    version="V1",
                    package_id="2",
                    status='INSTANTIATED').save()
        self.req_data = {
            "extVirtualLinks": [{
                "id": "string",
                "resourceId": "329efb86-5cbb-4fc0-bc7c-6ea28f9d7389",
                "resourceSubnetId": "429efb86-5cbb-4fc0-bc7c-6ea28f9d7389",
                "extCps": [{
                    "cpdId": "ext_cp",
                    "cpConfig": [{
                        "cpInstanceId": "",
                        "cpProtocolData": [{
                            "layerProtocol": "IP_OVER_ETHERNET",
                            "ipOverEthernet": {
                                "ipAddresses": [{
                                    "type": "IPV4",
                                    "numDynamicAddresses": 0,
                                    "subnetId": "59e9ffa9-b67e-4c05-b191-ed179007536e"
                                }]
                            }
                        }]
                    }]
                }],
                "extLinkPorts": []
            }],
            "vimConnectionInfo": [{
                "id": "tecs_RegionOne",
                "vimType": "openstack",
                "vimId": "tecs_RegionOne",
                "accessInfo": {
                    "tenant": "chinamobile"
                }
            }],
            "additionalParams": {
                "vmid": "552ea058-6441-4de5-b4c1-b0a52c7557e8"
            }
        }

    def tearDown(self):
        NfInstModel.objects.filter(nfinstid='12345').delete()
        NfInstModel.objects.filter(nfinstid='123').delete()

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(
            jobid=job_id,
            progress=job_progress,
            descp=job_detail
        )
        self.assertEqual(1, len(jobs))

    def test_change_ext_conn_not_found(self):
        url = "/api/vnflcm/v1/vnf_instances/12/change_ext_conn"
        response = self.client.post(url,
                                    data=self.req_data,
                                    format='json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_change_ext_conn_conflict(self):
        url = "/api/vnflcm/v1/vnf_instances/12345/change_ext_conn"
        response = self.client.post(url,
                                    data=self.req_data,
                                    format='json')
        self.assertEqual(status.HTTP_409_CONFLICT, response.status_code)

    def test_change_ext_conn_badreq(self):
        url = "/api/vnflcm/v1/vnf_instances/123/change_ext_conn"
        response = self.client.post(url,
                                    data={},
                                    format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock.patch.object(JobUtil, 'create_job')
    def test_change_ext_conn_inner_error(self, mock_run):
        mock_run.return_value = NFLCMException('Boom!')
        url = "/api/vnflcm/v1/vnf_instances/123/change_ext_conn"
        response = self.client.post(url,
                                    data=self.req_data,
                                    format='json')
        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.status_code)

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_change_ext_conn_sucess(self, mock_call, mock_call_req):
        self.nf_inst_id = '12345'
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
            const.c6_data_create_port
        ]
        self.job_id = JobUtil.create_job('NF', 'VNF_CHANGE_EXT_CONN', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, "VNF_'VNF_CHANGE_EXT_CONN'_READY")

        ChangeExtConn(self.req_data, self.nf_inst_id, self.job_id,).run()

        print([{job.progress: job.descp} for job in JobStatusModel.objects.filter(jobid=self.job_id)])
        self.assert_job_result(
            self.job_id,
            100,
            'Change ext conn success.'
        )
