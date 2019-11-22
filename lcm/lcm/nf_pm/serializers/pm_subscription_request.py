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
from lcm.nf_pm.counst import NOTIFICATION_TYPE, AUTH_TYPE


class VnfInstanceSubscriptionFilterSerializer(serializers.Serializer):
    vnfdIds = serializers.ListSerializer(help_text="If present, match VNF instances that were created based"
                                                   " on aVNFD identified by one of the vnfdId values listed"
                                                   " in this attribute.",
                                         required=False, allow_null=True, many=True)
    vnfProductsFromProviders = serializers.ListSerializer(help_text="If present, match VNF instances that "
                                                                    "belong to VNF products from certain"
                                                                    " providers.",
                                                          required=False, allow_null=True, many=True)
    vnfInstanceIds = serializers.ListSerializer(help_text="If present, match VNF instances with an instance "
                                                          "identifier listed in this attribute.",
                                                required=False, allow_null=True, many=True)
    vnfInstanceNames = serializers.ListSerializer(help_text="If present, match VNF instances with a VNF "
                                                            "Instance Name listed in this attribute.",
                                                  required=False, allow_null=True, many=True)


class PmNotificationsFilterSerializer(serializers.Serializer):
    vnfInstanceSubscriptionFilter = VnfInstanceSubscriptionFilterSerializer(
        help_text="Filter criteria to select VNF instances about which to notify.",
        required=False, allow_null=True)
    notificationTypes = serializers.ChoiceField(
        help_text="Match particular notification types.",
        required=False, allow_null=True,
        choices=NOTIFICATION_TYPE
    )


class SubscriptionAuthenticationSerializer(serializers.Serializer):
    authType = serializers.ChoiceField(help_text="Defines the types of Authentication / Authorization which"
                                                 " the API consumer is willing to accept when "
                                                 "receiving a notification.", required=True, allow_null=False,
                                       choices=AUTH_TYPE)
    paramsBasic = serializers.CharField(help_text="Parameters for authentication/authorization using BASIC.",
                                        required=False, allow_null=True)
    paramsOauth2ClientCredentials = serializers.CharField(help_text="Parameters for authentication/"
                                                                    "authorization using OAUTH2_CLIENT_"
                                                                    "CREDENTIALS.",
                                                          required=False, allow_null=True)


class PmSubscriptionRequestSerializer(serializers.Serializer):
    filter = PmNotificationsFilterSerializer(help_text="Filter settings for this subscription, to define the "
                                                       "subset of all notifications this"
                                                       " subscription relates to.",
                                             required=False, allow_null=True)
    callbackUri = serializers.CharField(help_text="The URI of the endpoint to send the notification to.",
                                        required=True, allow_null=False)
    authentication = SubscriptionAuthenticationSerializer(help_text="Authentication parameters to configure"
                                                                    " the use of Authorization when sending"
                                                                    " notifications corresponding to this"
                                                                    " subscription,",
                                                          required=False, allow_null=True)
