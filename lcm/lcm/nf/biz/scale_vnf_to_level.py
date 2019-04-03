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
import logging

from lcm.nf.biz.scale_vnf import ScaleVnf
from lcm.nf.const import GRANT_TYPE
from lcm.pub.database.models import VmInstModel
from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)


class ScaleVnfToLevel(ScaleVnf):
    def __init__(self, data, nf_inst_id, job_id):
        super(ScaleVnfToLevel, self).__init__(data=data,
                                              nf_inst_id=nf_inst_id,
                                              job_id=job_id)
        self.aspect_id = ''

    def scale_pre(self):
        self.vnfd_info = json.loads(self.vnf_insts[0].vnfd_model)
        scale_in_vms = VmInstModel.objects.filter(instid=self.nf_inst_id)
        vms_num = scale_in_vms.count()
        self.instantiation_level_id = self.data.get("instantiationLevelId")
        self.additional_params = self.data.get("additionalParams", {})
        if not self.instantiation_level_id:
            self.scale_info = self.data.get("scaleInfo")
            self.aspect_id = self.scale_info.get("aspectId")
            self.instantiation_level_id = self.get_instantiation_level_id()
        else:
            self.aspect_id = self.get_aspect_id()

        number_of_instances = self.get_number_of_instances()
        if number_of_instances == vms_num:
            raise NFLCMException("Don't need scale in/out.")
        elif number_of_instances > vms_num:
            self.scale_type = GRANT_TYPE.SCALE_OUT
        else:
            self.scale_type = GRANT_TYPE.SCALE_IN

        self.scale_inst_num = abs(number_of_instances - vms_num)
        self.is_scale_in = (self.scale_type == GRANT_TYPE.SCALE_IN)
        self.step_delta = self.get_scale_step_delta()
        self.target_vdu, self.step_inst_num = self.get_vdu_scale_aspect_deltas()
        self.min_instance_num, self.max_instance_num = self.get_instance_range()
        self.check_if_can_scale()
        self.scale_out_resource = {}

    def get_number_of_instances(self):
        for policy in self.vnfd_info.get("policies", []):
            if policy.get("type") != "tosca.policies.nfv.VduInstantiationLevels":
                continue
            # if not self.aspect_id:
            #     self.aspect_id = policy.get("targets")[0]
            levels = policy["properties"]["levels"]
            number_of_instances = levels.get(self.instantiation_level_id)
            if number_of_instances:
                return number_of_instances.get("number_of_instances")
        raise NFLCMException("InstantiationLevelId(%s) does not exist" % self.instantiation_level_id)

    def get_instantiation_level_id(self):
        scale_level_in_request = self.scale_info.get("scaleLevel")
        for policy in self.vnfd_info.get("policies", []):
            if policy.get("type") != "tosca.policies.nfv.InstantiationLevels":
                continue
            levels = policy["properties"]["levels"]
            for level_id, level_info in levels.items():
                scale_aspect = level_info["scale_info"].get(self.aspect_id)
                scale_level_in_vnfd = scale_aspect["scale_level"]
                if scale_level_in_request == scale_level_in_vnfd:
                    return level_id
        raise NFLCMException("Failed to get scale_info in vnfd")

    def get_aspect_id(self):
        for policy in self.vnfd_info.get("policies", []):
            if policy.get("type") != "tosca.policies.nfv.InstantiationLevels":
                continue
            levels = policy["properties"]["levels"]
            level_info = levels.get(self.instantiation_level_id)
            return level_info.get("scale_info").keys()[0]
        raise NFLCMException("Failed to get aspect_id in vnfd")
