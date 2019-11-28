# Copyright (c) 2019, CMCC Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License")
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

from rest_framework import serializers

from lcm.nf_pm.serializers.create_pm_job_request import PmJobCriteriaSerializer


class PmJob(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this PM job.", required=True, allow_null=False)
    objectInstanceIds = serializers.ListField(help_text="Identifiers of the VNF instances for which "
                                                        "performance information is collected",
                                              required=True, allow_null=False)
    criteria = PmJobCriteriaSerializer(help_text="Criteria of the collection of performance information.",
                                       required=True, allow_null=False)
    reports = serializers.ListField(help_text="Information about available reports collected by this PM job.",
                                    required=False, allow_null=True)
    