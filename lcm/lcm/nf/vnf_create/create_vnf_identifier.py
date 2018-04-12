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
import traceback
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
        try:
            self.check_valid()
            self.save_db()
        except NFLCMException as e:
            logger.debug('Create VNF instance[%s]: %s', self.nf_inst_id, e.message)
            raise NFLCMException(e.message)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            NfInstModel.objects.create(nfinstid=self.nf_inst_id,
                                       nf_name=self.vnf_instance_mame,
                                       package_id='',
                                       version='',
                                       vendor='',
                                       netype='',
                                       vnfd_model='',
                                       status='NOT_INSTANTIATED',
                                       nf_desc=self.description,
                                       vnfdid=self.csar_id,
                                       vnfSoftwareVersion='',
                                       create_time=now_time())
        vnf_inst = NfInstModel.objects.get(nfinstid=self.nf_inst_id)
        resp = {
            'id': vnf_inst.nfinstid,
            'vnfInstanceName': vnf_inst.nf_name,
            'vnfInstanceDescription': 'Human-readable description of the VNF instance.',
            'vnfdId': vnf_inst.vnfdid,
            'vnfProvider': vnf_inst.vendor,
            'vnfProductName': vnf_inst.nf_name,
            'vnfSoftwareVersion': vnf_inst.vnfSoftwareVersion,
            'vnfdVersion': vnf_inst.version,
            'vnfPkgId': vnf_inst.package_id,
            'vnfConfigurableProperties': {}
        }
        return resp

    def check_valid(self):
        is_exist = NfInstModel.objects.filter(nf_name=self.vnf_instance_mame).exists()
        if is_exist:
            raise NFLCMException('VNF is already exist.')
        vnf_package_info = query_vnfpackage_by_id(self.csar_id)
        self.vnfd_info = json.loads(ignore_case_get(ignore_case_get(vnf_package_info, "packageInfo"), "vnfdModel"))

    def save_db(self):
        metadata = ignore_case_get(self.vnfd_info, "metadata")
        version = ignore_case_get(metadata, "vnfdVersion")
        vendor = ignore_case_get(metadata, "vendor")
        netype = ignore_case_get(metadata, "type")
        vnfsoftwareversion = ignore_case_get(metadata, "version")
        NfInstModel.objects.create(nfinstid=self.nf_inst_id,
                                   nf_name=self.vnf_instance_mame,
                                   package_id=self.csar_id,
                                   version=version,
                                   vendor=vendor,
                                   netype=netype,
                                   vnfd_model=self.vnfd_info,
                                   status='NOT_INSTANTIATED',
                                   nf_desc=self.description,
                                   vnfdid=self.csar_id,
                                   vnfSoftwareVersion=vnfsoftwareversion,
                                   create_time=now_time())
        logger.debug('Create VNF instance[%s] success', self.nf_inst_id)
