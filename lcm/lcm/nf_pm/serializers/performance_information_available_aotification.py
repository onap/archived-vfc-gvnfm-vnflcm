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

from lcm.nf_pm.serializers.Link import LinkSerializer


class PerformanceInformationAvailableNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this notification.", required=True, allow_null=False)
    notificationType = serializers.CharField(help_text="Discriminator for the different notification types.",
                                             required=True, allow_null=False)
    subscriptionId = serializers.CharField(help_text="Identifier of the subscription that this notification "
                                                     "relates to.", required=True, allow_null=False)
    timeStamp = serializers.DateField(help_text="Date and time of the generation of thenotification.",
                                      required=True, allow_null=False)
    objectInstanceId = serializers.CharField(help_text="Identifier that identifies a VNF instance.",
                                             required=True, allow_null=False)
    _links = LinkSerializer(help_text="Links to resources related to this notification",
                            required=True, allow_null=False)
