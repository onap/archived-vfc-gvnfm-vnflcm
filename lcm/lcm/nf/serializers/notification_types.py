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

from affected_vnfcs import AffectedVnfcsSerializer
from affected_vls import AffectedVLsSerializer
from affected_storages import AffectedStoragesSerializer
from lcm.nf.const import LCM_OPERATION_TYPES, LCM_OPERATION_STATE_TYPES
from link import LinkSerializer
from response import ProblemDetailsSerializer
from ext_virtual_link_info import ExtVirtualLinkInfoSerializer
from vnf_info_modifications import VnfInfoModificationsSerializer


class LccnLinksSerializer(serializers.Serializer):
    vnfInstance = LinkSerializer(
        help_text="Link to the resource representing the VNF instance to "
        "which the notified change applies.",
        required=True,
        allow_null=False)
    subscription = LinkSerializer(
        help_text="Link to the related subscription.",
        required=True,
        allow_null=False)
    vnfLcmOpOcc = LinkSerializer(
        help_text="Link to the VNF lifecycle management operation"
        "occurrence that this notification is related to. Shall be"
        "present if there is a related lifecycle operation occurance.",
        required=False,
        allow_null=False)


class VnfLcmOperationOccurrenceNotification(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this notification",
        max_length=255,
        required=True,
        allow_null=False)
    notificationType = serializers.CharField(
        help_text="Type of the notification",
        max_length=50,
        required=True,
        allow_null=False)
    subscriptionId = serializers.CharField(
        help_text="Identifier for the subscription",
        required=False)
    timeStamp = serializers.CharField(
        help_text="Date-time of the generation of the notification.",
        required=True)
    notificationStatus = serializers.ChoiceField(
        help_text="Indicates whether this notification reports about the start"
        "of a lifecycle operation or the result of a lifecycle"
        "operation",
        choices=["START", "RESULT"],
        required=True)
    operationState = serializers.ChoiceField(
        choices=LCM_OPERATION_STATE_TYPES,
        help_text="The state of the VNF LCM operation occurrence. ",
        required=True)
    vnfInstanceId = serializers.CharField(
        help_text="The identifier of the VNF instance affected. ",
        required=True)
    operation = serializers.ChoiceField(
        help_text="The lifecycle management operation.",
        required=True,
        choices=LCM_OPERATION_TYPES)
    isAutomaticInvocation = serializers.BooleanField(
        help_text="Set to true if this VNF LCM operation occurrence has"
        "been triggered by an automated procedure inside the"
        "VNFM. Otherwise False",
        required=True)
    vnfLcmOpOccId = serializers.CharField(
        help_text="The identifier of the VNF lifecycle management"
        "operation occurrence associated to the notification.",
        required=True)
    affectedVnfcs = AffectedVnfcsSerializer(
        help_text="Information about VNFC instances that were affected " +
        "during the lifecycle operation.",
        required=False,
        many=True
    )
    affectedVirtualLinks = AffectedVLsSerializer(
        help_text="Information about VL instances that were affected " +
        "during the lifecycle operation. ",
        required=False,
        many=True
    )
    affectedVirtualStorages = AffectedStoragesSerializer(
        help_text="Information about virtualised storage instances that " +
        "were affected during the lifecycle operation",
        required=False,
        many=True
    )
    changedInfo = VnfInfoModificationsSerializer(
        help_text="Information about the changed VNF instance information, " +
        "including VNF configurable properties",
        required=False,
        allow_null=True)
    changedExtConnectivity = ExtVirtualLinkInfoSerializer(
        help_text="Information about changed external connectivity, if this " +
        "notification represents the result of a lifecycle operation occurrence. " +
        "Shall be present if the 'notificationStatus' is set to 'RESULT' and the " +
        "'operation' is set to 'CHANGE_EXT_CONN'. Shall be absent otherwise.",
        many=True,
        required=False,
        allow_null=True)
    error = ProblemDetailsSerializer(
        help_text="If 'operationState' is 'FAILED_TEMP' or 'FAILED' or " +
        "'PROCESSING' or 'ROLLING_BACK' and previous value of 'operationState' " +
        "was 'FAILED_TEMP'  this attribute shall be present ",
        allow_null=True,
        required=False
    )
    _links = LccnLinksSerializer(
        help_text="Links to resources related to this resource.",
        required=True)
