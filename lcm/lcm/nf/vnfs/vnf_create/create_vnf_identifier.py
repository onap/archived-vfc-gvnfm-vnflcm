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
from lcm.pub.utils.restcall import req_by_msb
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)
# Query vnfd_rawdata by vnfdid
def vnfd_rawdata_get(vnfdid):
    ret = req_by_msb("openoapi/nslcm/v1/vnfpackage/%s" % vnfdid, "GET")
    return ret

class CreateVnf:
    def __init__(self, data):
        self.data = data

    def do_biz(self):
        logger.debug("CreateVnfIdentifier--CreateVnf::> %s" % self.data)
        self.vnfd_id = ignore_case_get(self.data, "vnfdId")
        self.vnf_instance_mame = ignore_case_get(self.data, "vnfInstanceName")
        self.description = ignore_case_get(self.data, "vnfInstanceDescription")
        is_exist = NfInstModel.objects.filter(nf_name=self.vnf_instance_mame).exists()
        logger.debug("check_ns_inst_name_exist::is_exist=%s" % is_exist)
        if is_exist:
            raise NFLCMException('VNF is already exist.')

        #get rawdata by vnfd_id
        ret = vnfd_rawdata_get(self.vnfd_id)
        if ret[0] != 0:
            raise NFLCMException('Get vnfd_raw_data failed.')
        dst_plan = json.JSONDecoder().decode(ret[1])
        self.vnfd_version = dst_plan['metadata']['vnfd_version']
        self.vendor = dst_plan['metadata']['vendor']
        self.producttype = dst_plan['metadata']['domain_type']
        self.netype = dst_plan['metadata']['vnf_type']
        self.vnfd_model = dst_plan
        self.vnfSoftwareVersion = dst_plan['metadata']['version']

        self.nf_inst_id = str(uuid.uuid4())
        NfInstModel.objects.create(nfinstid=self.nf_inst_id, mnfinstid=self.nf_inst_id, nf_name=self.vnf_instance_mame,
                                   package_id='todo', vnfm_inst_id='todo', version=self.vnfd_version, vendor=self.vendor,
                                   producttype=self.producttype,netype=self.netype, vnfd_model=self.vnfd_model,
                                   instantiationState='NOT_INSTANTIATED', nf_desc=self.description, vnfdid=self.vnfd_id,
                                   vnfSoftwareVersion=self.vnfSoftwareVersion, vnfConfigurableProperties='todo',
                                   localizationLanguage='EN_US',create_time=now_time())
        is_exist = NfInstModel.objects.filter(nf_name=self.vnf_instance_mame).exists()
        logger.debug("check_ns_inst_name_exist::is_exist=%s" % is_exist)
        return self.nf_inst_id