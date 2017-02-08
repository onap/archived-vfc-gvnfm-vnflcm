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

import logging
import uuid

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.pub.database.models import VnfInstModel
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class CreateVnfIdentifier(APIView):
    def post(self, request):
        logger.debug("CreateVnfIdentifier--post::> %s" % request.data)
        self.vnfd_id = ignore_case_get(request.data, "vnfdId")
        self.vnf_instance_mame = ignore_case_get(request.data, "vnfInstanceName")
        self.description = ignore_case_get(request.data, "vnfInstanceDescription")
        self.nf_inst_id = str(uuid.uuid4())
        VnfInstModel(id=self.nf_inst_id, name=self.vnf_instance_mame, vnfd_id=self.vnfd_id,
                     description=self.description, status='empty', create_time=now_time(), lastuptime=now_time()).save()
        vnf_inst = VnfInstModel.objects.get(id=self.nf_inst_id)
        logger.debug('id is [%s],name is [%s],vnfd_id is [%s],description is [%s],create_time is [%s],lastuptime is [%s],' %
                     (vnf_inst.id, vnf_inst.name, vnf_inst.vnfd_id, vnf_inst.description, vnf_inst.create_time, vnf_inst.lastuptime))
        rsp = {"vnfInstanceId": self.nf_inst_id}
        return Response(data=rsp, status=status.HTTP_201_CREATED)


class InstantiateVnf(APIView):
    def post(self, request, instanceId):
        logger.debug("InstantiateVnf--post::> %s" % request.data)
        data = {'flavourId': ignore_case_get(request.data, 'flavourId'),
                'instantiationLevelId': ignore_case_get(request.data, 'instantiationLevelId'),
                'extVirtualLinks': ignore_case_get(request.data, 'extVirtualLinks'),
                'localizationLanguage': ignore_case_get(request.data, 'localizationLanguage'),
                'additionalParams': ignore_case_get(request.data, 'additionalParams')}
        nf_inst_id = instanceId
        job_id = JobUtil.create_job('NF', 'CREATE', nf_inst_id)
        JobUtil.add_job_status(job_id, 0, "INST_VNF_READY")

        # CreateVnfs(data, nf_inst_id, job_id).start()
        rsp = {"jobId": job_id}
        return Response(data=rsp, status=status.HTTP_202_ACCEPTED)