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

from .const import c1_data_get_tenant_id
from .const import c4_data_create_network
from .const import c2_data_create_volume
from .const import c5_data_create_subnet
from .const import c3_data_get_volume
from .const import c6_data_create_port
from .const import c7_data_create_flavor
from .const import c8_data_list_image
from .const import c9_data_create_vm
from .const import c10_data_get_vm
from .const import inst_req_data
from .const import vnfpackage_info
from .const import instantiate_grant_result

from lcm.pub.database.models import NfInstModel, VNFLcmOpOccModel
from lcm.pub.database.models import JobStatusModel
from lcm.pub.database.models import SubscriptionModel
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.notificationsutil import NotificationsUtil
from lcm.pub.vimapi import api
from lcm.pub.exceptions import NFLCMException

from lcm.nf.biz.instantiate_vnf import InstantiateVnf
from lcm.nf import const


class TestNFInstantiate(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.grant_result = instantiate_grant_result

    def tearDown(self):
        NfInstModel.objects.all().delete()

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(
            jobid=job_id,
            progress=job_progress,
            descp=job_detail
        )
        self.assertEqual(1, len(jobs))

    @mock.patch.object(InstantiateVnf, 'run')
    def test_instantiate_vnf(self, mock_run):
        NfInstModel(
            nfinstid='12',
            nf_name='VNF1',
            status='NOT_INSTANTIATED'
        ).save()
        mock_run.re.return_value = None
        response = self.client.post(
            '/api/vnflcm/v1/vnf_instances/12/instantiate',
            data=inst_req_data,
            format='json'
        )
        self.assertEqual(
            status.HTTP_202_ACCEPTED,
            response.status_code
        )

    @mock.patch.object(InstantiateVnf, 'run')
    def test_instantiate_vnf_notfound(self, mock_run):
        mock_run.re.return_value = None
        response = self.client.post(
            '/api/vnflcm/v1/vnf_instances/3421/instantiate',
            data=inst_req_data,
            format='json'
        )
        self.assertEqual(
            status.HTTP_404_NOT_FOUND,
            response.status_code,
            response.content
        )

    @mock.patch.object(InstantiateVnf, 'run')
    def test_instantiate_vnf_conflict(self, mock_run):
        NfInstModel(
            nfinstid='1123',
            nf_name='VNF1',
            status='INSTANTIATED'
        ).save()
        mock_run.re.return_value = None
        response = self.client.post(
            '/api/vnflcm/v1/vnf_instances/1123/instantiate',
            data=inst_req_data,
            format='json'
        )
        self.assertEqual(
            status.HTTP_409_CONFLICT,
            response.status_code,
            response.content
        )

    def test_instantiate_vnf_when_inst_id_not_exist(self):
        self.nf_inst_id = str(uuid.uuid4())
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, 'INST_VNF_READY')
        jobs = JobStatusModel.objects.filter(
            jobid=self.job_id,
            progress=0,
            descp='INST_VNF_READY'
        )
        self.assertEqual(1, len(jobs))
        data = inst_req_data
        InstantiateVnf(
            data,
            nf_inst_id=self.nf_inst_id,
            job_id=self.job_id
        ).run()
        self.assert_job_result(
            self.job_id,
            255,
            'VNF nf_inst_id is not exist.'
        )

    def test_instantiate_vnf_when_already_instantiated(self):
        NfInstModel.objects.create(
            nfinstid='1111',
            nf_name='vFW_01',
            package_id='222',
            version='',
            vendor='',
            netype='',
            vnfd_model='',
            status='INSTANTIATED',
            nf_desc='vFW in Nanjing TIC Edge',
            vnfdid='111',
            create_time=now_time()
        )
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, 'INST_VNF_READY')
        jobs = JobStatusModel.objects.filter(
            jobid=self.job_id,
            progress=0,
            descp='INST_VNF_READY'
        )
        self.assertEqual(1, len(jobs))
        data = inst_req_data
        InstantiateVnf(
            data,
            nf_inst_id=self.nf_inst_id,
            job_id=self.job_id
        ).run()
        self.assert_job_result(
            self.job_id,
            255,
            'VNF instantiationState is not NOT_INSTANTIATED.'
        )

    @mock.patch.object(restcall, 'call_req')
    def test_instantiate_vnf_when_get_packageinfo_by_csarid_failed(self, mock_call_req):
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
        r1_get_vnfpackage_by_vnfdid = [
            1,
            json.JSONEncoder().encode(vnfpackage_info),
            '200'
        ]
        mock_call_req.side_effect = [r1_get_vnfpackage_by_vnfdid]
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, 'INST_VNF_READY')
        data = inst_req_data
        InstantiateVnf(
            data,
            nf_inst_id=self.nf_inst_id,
            job_id=self.job_id
        ).run()
        self.assert_job_result(
            self.job_id,
            255,
            'Failed to query vnf CSAR(111) from catalog.'
        )

    @mock.patch.object(restcall, 'call_req')
    def test_instantiate_vnf_when_applay_grant_failed(self, mock_call_req):
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
        r1_get_vnfpackage_by_vnfdid = [
            0,
            json.JSONEncoder().encode(vnfpackage_info),
            '200'
        ]
        r2_apply_grant_result = [
            1,
            json.JSONEncoder().encode(self.grant_result),
            '200'
        ]
        mock_call_req.side_effect = [
            r1_get_vnfpackage_by_vnfdid,
            r2_apply_grant_result
        ]
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, 'INST_VNF_READY')
        data = inst_req_data
        InstantiateVnf(
            data,
            nf_inst_id=self.nf_inst_id,
            job_id=self.job_id
        ).run()
        self.assert_job_result(
            self.job_id,
            255,
            'Nf instancing apply grant exception'
        )

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    def test_instantiate_vnf_when_unexpected_exception(self, mock_call, mock_call_req):
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
        r1_get_vnfpackage_by_vnfdid = [
            0,
            json.JSONEncoder().encode(vnfpackage_info),
            '200'
        ]
        r2_apply_grant_result = [
            0,
            json.JSONEncoder().encode(self.grant_result),
            '200'
        ]
        mock_call_req.side_effect = [
            r1_get_vnfpackage_by_vnfdid,
            r2_apply_grant_result
        ]
        mock_call.side_effect = [
            c1_data_get_tenant_id,
            c2_data_create_volume,
            c3_data_get_volume
        ]
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, 'INST_VNF_READY')
        data = inst_req_data
        InstantiateVnf(
            data,
            nf_inst_id=self.nf_inst_id,
            job_id=self.job_id
        ).run()
        self.assert_job_result(
            self.job_id,
            255,
            'unexpected exception'
        )

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(api, 'call')
    @mock.patch.object(NotificationsUtil, 'post_notification')
    def test_instantiate_vnf_success(self, mock_post_notification, mock_call, mock_call_req):
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
        SubscriptionModel.objects.create(
            subscription_id=str(uuid.uuid4()),
            callback_uri='api/gvnfmdriver/v1/vnfs/lifecyclechangesnotification',
            auth_info=json.JSONEncoder().encode({
                'authType': ['BASIC'],
                'paramsBasic': {
                    'userName': 'username',
                    'password': 'password'
                }
            }),
            notification_types=str([
                'VnfLcmOperationOccurrenceNotification',
                'VnfIdentifierCreationNotification',
                'VnfIdentifierDeletionNotification'
            ]),
            operation_types=str(['INSTANTIATE']),
            operation_states=str(['COMPLETED']),
            vnf_instance_filter=json.JSONEncoder().encode({
                'vnfdIds': ['111'],
                'vnfProductsFromProviders': [],
                'vnfInstanceIds': ['1111'],
                'vnfInstanceNames': [],
            })
        )
        r1_get_vnfpackage_by_vnfdid = [
            0,
            json.JSONEncoder().encode(vnfpackage_info),
            '200'
        ]
        r2_apply_grant_result = [
            0,
            json.JSONEncoder().encode(self.grant_result),
            '200'
        ]
        r3_all_aai_result = [
            1,
            json.JSONEncoder().encode(''),
            '404'
        ]
        r4_lcm_notify_result = [
            0,
            json.JSONEncoder().encode(''),
            '200'
        ]
        mock_call_req.side_effect = [
            r1_get_vnfpackage_by_vnfdid,
            r2_apply_grant_result,
            r3_all_aai_result,
            r4_lcm_notify_result
        ]
        mock_call.side_effect = [
            c1_data_get_tenant_id,
            c2_data_create_volume,
            c3_data_get_volume,
            c4_data_create_network,
            c5_data_create_subnet,
            c6_data_create_port,
            c7_data_create_flavor,
            c8_data_list_image,
            c9_data_create_vm,
            c10_data_get_vm
        ]
        mock_post_notification.side_effect = None
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, 'INST_VNF_READY')
        data = inst_req_data
        InstantiateVnf(
            data,
            nf_inst_id=self.nf_inst_id,
            job_id=self.job_id
        ).run()
        self.assert_job_result(
            self.job_id,
            100,
            'Instantiate Vnf success.'
        )

    @mock.patch.object(JobUtil, 'create_job')
    def test_instantiate_inner_error(self, mock_run):
        NfInstModel(
            nfinstid='144',
            nf_name='VNF1',
            status='NOT_INSTANTIATED'
        ).save()
        mock_run.return_value = NFLCMException('Boom!')
        response = self.client.post(
            '/api/vnflcm/v1/vnf_instances/144/instantiate',
            data=inst_req_data,
            format='json'
        )
        NfInstModel.objects.filter(nfinstid='144').delete()
        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)

    def test_instantiate_badreq(self):
        NfInstModel(
            nfinstid='144',
            nf_name='VNF1',
            status='NOT_INSTANTIATED'
        ).save()
        response = self.client.post(
            '/api/vnflcm/v1/vnf_instances/144/instantiate',
            data={},
            format='json'
        )
        NfInstModel.objects.filter(nfinstid='144').delete()
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock.patch.object(restcall, 'call_req')
    def test_instantiate_operating_fail(self, mock_call_req):
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
        r1_get_vnfpackage_by_vnfdid = [
            0,
            json.JSONEncoder().encode(vnfpackage_info),
            '200'
        ]
        mock_call_req.side_effect = [
            r1_get_vnfpackage_by_vnfdid
        ]
        self.nf_inst_id = '1111'
        self.job_id = JobUtil.create_job('NF', 'CREATE', self.nf_inst_id)
        JobUtil.add_job_status(self.job_id, 0, 'INST_VNF_READY')
        VNFLcmOpOccModel.objects.create(vnf_instance_id=self.nf_inst_id,
                                        id=self.job_id,
                                        operation=const.OPERATION_TYPE.INSTANTIATE,
                                        operation_state=const.OPERATION_STATE_TYPE.PROCESSING)
        InstantiateVnf(
            inst_req_data,
            nf_inst_id=self.nf_inst_id,
            job_id=self.job_id
        ).run()
        self.assert_job_result(
            self.job_id,
            255,
            'VNF(%s) %s in processing.' % (self.nf_inst_id, const.OPERATION_TYPE.INSTANTIATE)
        )
