# Copyright (C) 2018 Verizon. All Rights Reserved
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

from rest_framework import serializers

from .vnf_instance_subscription_filter import VnfInstanceSubscriptionFilter
from lcm.nf.const import NOTIFICATION_TYPES, LCM_OPERATION_TYPES, LCM_OPERATION_STATE_TYPES


class LifeCycleChangeNotificationsFilter(serializers.Serializer):
    notificationTypes = serializers.ListField(
        child=serializers.ChoiceField(required=True, choices=NOTIFICATION_TYPES),
        help_text="Match particular notification types",
        allow_null=False,
        required=False)
    operationTypes = serializers.ListField(
        child=serializers.ChoiceField(required=True, choices=LCM_OPERATION_TYPES),
        help_text="Match particular VNF lifecycle operation types for the " +
        "notification of type VnfLcmOperationOccurrenceNotification.",
        allow_null=False,
        required=False)
    operationStates = serializers.ListField(
        child=serializers.ChoiceField(required=True, choices=LCM_OPERATION_STATE_TYPES),
        help_text="Match particular LCM operation state values as reported " +
        "in notifications of type VnfLcmOperationOccurrenceNotification.",
        allow_null=False,
        required=False)
    vnfInstanceSubscriptionFilter = VnfInstanceSubscriptionFilter(
        help_text="Filter criteria to select VNF instances about which to notify.",
        required=False,
        allow_null=False)
