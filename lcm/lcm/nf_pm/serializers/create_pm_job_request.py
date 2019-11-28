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


class PmJobCriteriaSerializer(serializers.Serializer):
    performanceMetric = serializers.ListField(help_text="This defines the types of performance metrics "
                                                        "for the specified object instances, as specified "
                                                        "in an external measurement specification",
                                              required=False, allow_null=True)
    performanceMetricGroup = serializers.ListField(help_text="Group of performance metrics",
                                                   required=False, allow_null=True)
    collectionPeriod = serializers.CharField(help_text="Specifies the periodicity at which the producer "
                                                       "will collect performance information",
                                             required=True, allow_null=False)
    reportingPeriod = serializers.CharField(help_text="Specifies the periodicity at which the producer "
                                                      "will report to the consumer",
                                            required=True, allow_null=False)
    reportingBoundary = serializers.DateField(help_text="dentifies a time boundary after which the reporting "
                                                        "will stop.", required=False, allow_null=True)


class CreatePmJobRequestSerializer(serializers.Serializer):
    objectInstanceIds = serializers.ListField(help_text="Identifiers of the VNF instances for which "
                                                        "performance information is requested to be "
                                                        "collected.", required=True, allow_null=False)
    criteria = PmJobCriteriaSerializer(help_text="Criteria of the collection of performance information",
                                       required=True, allow_null=False)
