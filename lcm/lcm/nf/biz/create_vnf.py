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
import logging
import uuid

from lcm.pub.database.models import NfInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.msapi.sdc_run_catalog import query_vnfpackage_by_id
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class CreateVnf:
    def __init__(self, data):
        self.data = data
        self.csar_id = ignore_case_get(self.data, "vnfdId")
        self.vnf_instance_mame = ignore_case_get(self.data, "vnfInstanceName")
        self.description = ignore_case_get(self.data, "vnfInstanceDescription")

    def do_biz(self):
        self.nf_inst_id = str(uuid.uuid4())
        self.check_valid()
        self.save_db()
        vnf_inst = NfInstModel.objects.get(nfinstid=self.nf_inst_id)
        return vnf_inst

    def check_valid(self):
        is_exist = NfInstModel.objects.filter(nf_name=self.vnf_instance_mame).exists()
        if is_exist:
            raise NFLCMException('VNF is already exist.')
        vnf_package_info = query_vnfpackage_by_id(self.csar_id)
        self.vnfd_info = json.loads(ignore_case_get(ignore_case_get(vnf_package_info, "packageInfo"), "vnfdModel"))

    def save_db(self):
        metadata = ignore_case_get(self.vnfd_info, "metadata")
        version = ignore_case_get(metadata, "csarVersion")
        provider = ignore_case_get(metadata, "csarProvider")
        netype = ignore_case_get(metadata, "type")
        vnfsoftwareversion = ignore_case_get(metadata, "version")
        NfInstModel.objects.create(nfinstid=self.nf_inst_id,
                                   nf_name=self.vnf_instance_mame,
                                   package_id=self.csar_id,
                                   version=version,
                                   vendor=provider,
                                   netype=netype,
                                   vnfd_model=json.dumps(self.vnfd_info),
                                   status='NOT_INSTANTIATED',
                                   nf_desc=self.description,
                                   vnfdid=self.csar_id,
                                   vnfSoftwareVersion=vnfsoftwareversion,
                                   create_time=now_time())
        logger.debug('Create VNF instance[%s] success', self.nf_inst_id)
