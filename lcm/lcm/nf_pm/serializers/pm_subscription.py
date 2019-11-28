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
from lcm.nf_pm.serializers.pm_subscription_request import PmNotificationsFilterSerializer


class PmSubscriptionSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier that identifies the subscription",
                               required=True, allow_null=False)
    filter = PmNotificationsFilterSerializer(help_text="Filter settings for this subscription, to define the"
                                                       " subset of all notifications this subscription "
                                                       "relates to.", required=False, allow_null=True)
    callbackUri = serializers.CharField(help_text="The URI of the endpoint to send the notification to",
                                        required=True, allow_null=False)
    _links = LinkSerializer(
        help_text="Links to resources related to this resource.",
        required=True,
        allow_null=False)
