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

from lcm.nf_pm.counst import THRESHOLDTYPE


class ThresholdCriteriaSerializer(serializers.Serializer):
    performanceMetric = serializers.CharField(help_text="Defines the performance metric associated with the"
                                                        "threshold, as specified in an external measurement"
                                                        "specification.", required=True, allow_null=False)
    thresholdType = serializers.ChoiceField(help_text="Type of threshold", required=True, allow_null=False,
                                            choices=THRESHOLDTYPE)
    simpleThresholdDetails = serializers.CharField(help_text="Details of a simple threshold",
                                                   required=False, allow_null=True)


class CreateThresholdRequestSerializer(serializers.Serializer):
    objectInstanceId = serializers.CharField(help_text="Identifier of the VNF instance associated with this "
                                                       "threshold.", required=True, allow_null=False)
    criteria = ThresholdCriteriaSerializer(help_text="Criteria that define this threshold.",
                                           required=True, allow_null=False)
