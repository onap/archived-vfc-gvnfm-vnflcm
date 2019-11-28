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

from lcm.nf_pm.counst import CrossingDirectionType
from lcm.nf_pm.serializers.Link import LinkSerializer


class ThresholdCrossedNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this notification.", required=True, allow_null=False)
    notificationType = serializers.CharField(help_text="Discriminator for the different notification types.",
                                             required=True, allow_null=False)
    subscriptionId = serializers.CharField(help_text="Identifier of the subscription that this notification "
                                                     "relates to", required=True, allow_null=False)
    timeStamp = serializers.DateField(help_text="Date and time of the generation of the notification",
                                      required=True, allow_null=False)
    thresholdId = serializers.CharField(help_text="Identifier of the threshold which has been crossed.",
                                        required=True, allow_null=False)
    crossingDirection = serializers.ChoiceField(help_text="An indication of whether the threshold was "
                                                          "crossed in upward or downward direction.",
                                                required=True, allow_null=False,
                                                choices=CrossingDirectionType)
    objectInstanceId = serializers.CharField(help_text="Identifier that identifies a VNF instance.",
                                             required=True, allow_null=False)
    performanceMetric = serializers.CharField(help_text="Performance metric associated with the threshold.",
                                              required=True, allow_null=False)
    performanceValue = serializers.CharField(help_text="Value of the metric that resulted in threshold "
                                                       "crossing.", required=True, allow_null=False)
    _links = LinkSerializer(help_text="Links to resources related to this notification",
                            required=True, allow_null=False)
