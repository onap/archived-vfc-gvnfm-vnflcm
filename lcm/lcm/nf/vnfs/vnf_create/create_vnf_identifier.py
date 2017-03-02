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
from lcm.pub.msapi.catalog import query_rawdata_from_catalog
from lcm.pub.msapi.nfvolcm import get_packageinfo_by_vnfdid
from lcm.pub.utils import toscautil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class CreateVnf:
    def __init__(self, data):
        self.data = data
        self.vnfd_id = ignore_case_get(self.data, "vnfdId")
        self.vnf_instance_mame = ignore_case_get(self.data, "vnfInstanceName")
        self.description = ignore_case_get(self.data, "vnfInstanceDescription")
        self.package_info = ''
        self.package_id = ''
        self.csar_id = ''

    def do_biz(self):
        logger.debug("CreateVnfIdentifier--CreateVnf::> %s" % self.data)
        is_exist = NfInstModel.objects.filter(nf_name=self.vnf_instance_mame).exists()
        logger.debug("check_inst_name_exist::is_exist=%s" % is_exist)
        if is_exist:
            raise NFLCMException('VNF is already exist.')

        nf_inst_id = str(uuid.uuid4())
        try:
            # get package_info from nslcm by vnfd_id
            self.package_info = get_packageinfo_by_vnfdid(self.vnfd_id)
            for val in self.package_info:
                if self.vnfd_id == ignore_case_get(val, "vnfd_id"):
                    self.package_id = ignore_case_get(val, "csar_id")
                    break

            # get rawdata from catalog by csar_id
            raw_data = query_rawdata_from_catalog(self.package_id, self.data)
            self.vnfd = toscautil.convert_vnfd_model(raw_data["rawData"])  # convert to inner json
            self.vnfd = json.JSONDecoder().decode(self.vnfd)

            metadata = ignore_case_get(self.vnfd, "metadata")
            version = ignore_case_get(metadata, "vnfd_version")
            vendor = ignore_case_get(metadata, "vendor")
            netype = ignore_case_get(metadata, "vnf_type")
            vnfsoftwareversion = ignore_case_get(metadata, "version")
            vnfd_model = self.vnfd
            NfInstModel.objects.create(nfinstid=nf_inst_id, nf_name=self.vnf_instance_mame, package_id=self.package_id,
                                       version=version, vendor=vendor, netype=netype, vnfd_model=vnfd_model,
                                       status='NOT_INSTANTIATED', nf_desc=self.description, vnfdid=self.vnfd_id,
                                       vnfSoftwareVersion=vnfsoftwareversion, create_time=now_time())
        except:
            NfInstModel.objects.create(nfinstid=nf_inst_id, nf_name=self.vnf_instance_mame, package_id='',
                                       version='', vendor='', netype='', vnfd_model='',
                                       status='NOT_INSTANTIATED', nf_desc=self.description, vnfdid=self.vnfd_id,
                                       vnfSoftwareVersion='', create_time=now_time())

        vnf_inst = NfInstModel.objects.get(nfinstid=nf_inst_id)
        logger.debug('id is [%s],name is [%s],vnfd_id is [%s],vnfd_model is [%s],description is [%s],create_time is [%s]' %
                     (vnf_inst.nfinstid, vnf_inst.nf_name, vnf_inst.vnfdid, vnf_inst.vnfd_model, vnf_inst.nf_desc, vnf_inst.create_time))
        return nf_inst_id
