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

from vnf_instance_subscription_filter import VnfInstanceSubscriptionFilter


NOTIFICATION_TYPES = [
    "VnfLcmOperationOccurrenceNotification",
    "VnfIdentifierCreationNotification",
    "VnfIdentifierDeletionNotification"]

LCM_OPERATION_TYPES = [
    "INSTANTIATE",
    "SCALE",
    "SCALE_TO_LEVEL",
    "CHANGE_FLAVOUR",
    "TERMINATE",
    "HEAL",
    "OPERATE",
    "CHANGE_EXT_CONN",
    "MODIFY_INFO"
]

LCM_OPERATION_STATE_TYPES = [
    "STARTING",
    "PROCESSING",
    "COMPLETED",
    "FAILED_TEMP",
    "FAILED",
    "ROLLING_BACK",
    "ROLLED_BACK"
]


def check_notification_types(notification_types):
    for notification_type in notification_types:
        if notification_type not in NOTIFICATION_TYPES:
            raise serializers.ValidationError(
                "%s is not valid " +
                "NOTIFICATION TYPE. Allowed values " +
                "are %s" % (notification_type, ",".join(NOTIFICATION_TYPES)))
    return notification_types


def check_operation_types(operation_types):
    for operation_type in operation_types:
        if operation_type not in LCM_OPERATION_TYPES:
            raise serializers.ValidationError(
                "%s is not valid " +
                "LCM OPERATION TYPE. Allowed values " +
                "are %s" % (operation_type, ",".join(LCM_OPERATION_TYPES)))
    return operation_types


def check_operation_states(operation_states):
    for operation_state in operation_states:
        if operation_state not in LCM_OPERATION_STATE_TYPES:
            raise serializers.ValidationError(
                "%s is not valid " +
                "OPERATION STATE. Allowed values " +
                "are %s" % (operation_state, ",".join(LCM_OPERATION_STATE_TYPES)))


class LccnFilterSerializer(serializers.Serializer):
    notificationTypes = serializers.ListField(
        child=serializers.CharField(required=True, max_length=255),
        help_text="Match particular notification types",
        allow_null=False,
        required=False,
        validators=[check_notification_types])
    operationTypes = serializers.ListField(
        child=serializers.CharField(required=True, max_length=255),
        help_text="Match particular VNF lifecycle operation types for the " +
        "notification of type VnfLcmOperationOccurrenceNotification.",
        allow_null=False,
        required=False,
        validators=[check_operation_types])
    operationStates = serializers.ListField(
        child=serializers.CharField(required=True, max_length=255),
        help_text="Match particular LCM operation state values as reported " +
        "in notifications of type VnfLcmOperationOccurrenceNotification.",
        allow_null=False,
        required=False,
        validators=[check_operation_states])
    vnfInstanceSubscriptionFilter = VnfInstanceSubscriptionFilter(
        help_text="Filter criteria to select VNF instances about which to notify.",
        required=False,
        allow_null=False)
