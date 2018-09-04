# Copyright (C) 2018 Verizon. All Rights Reserved.
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
from error_types import ProblemDetailsSerializer
from ext_virtual_link_info import ExtVirtualLinkInfoSerializer
from vnf_info_modifications import VnfInfoModificationsSerializer


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


class ResourceChangesSerializer(serializers.Serializer):
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


class LcmOpLinkSerializer(serializers.Serializer):
    self = serializers.CharField(
        help_text="URI of this resource.",
        max_length=255,
        required=True,
        allow_null=False)
    vnfInstance = serializers.CharField(
        help_text="Link to the VNF instance that the operation applies to.",
        required=True)
    grant = serializers.CharField(
        help_text="Link to the grant for this operation, if one exists.",
        required=False)
    cancel = serializers.CharField(
        help_text="Link to the task resource that represents the 'cancel' " +
        "operation for this VNF LCM operation occurrence.",
        required=False)
    retry = serializers.CharField(
        help_text="Link to the task resource that represents the 'retry' " +
        "operation for this VNF LCM operation occurrence, if" +
        " retrying is currently allowed",
        required=False)
    rollback = serializers.CharField(
        help_text="Link to the task resource that represents the 'cancel' " +
        "operation for this VNF LCM operation occurrence.",
        required=False)
    fail = serializers.CharField(
        help_text="Link to the task resource that represents the 'fail' " +
        "operation for this VNF LCM operation occurrence.",
        required=False)


class VNFLCMOpOccSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this VNF lifecycle management operation" +
        "occurrence,",
        max_length=255,
        required=True,
        allow_null=False
    )
    operationState = serializers.ChoiceField(
        help_text="The state of the VNF LCM operation occurrence. ",
        required=True,
        choices=LCM_OPERATION_STATE_TYPES
    )
    stateEnteredTime = serializers.CharField(
        help_text="Date-time when the current state was entered.",
        max_length=50
    )
    startTime = serializers.CharField(
        help_text="Date-time of the start of the operation.",
        max_length=50
    )
    vnfInstanceId = serializers.UUIDField(
        help_text="Identifier of the VNF instance to which the operation" +
        "applies"
    )
    grantId = serializers.UUIDField(
        help_text="Identifier of the grant related to this VNF LCM operation " +
                  "occurrence, if such grant exists.",
        allow_null=True
    )
    operation = serializers.ChoiceField(
        help_text="The lifecycle management operation",
        required=True,
        choices=LCM_OPERATION_TYPES
    )
    isAutomaticInvocation = serializers.BooleanField(
        help_text="Set to true if this VNF LCM operation occurrence has " +
        "been triggered by an automated procedure inside the VNFM. " +
        "Set to False otherwise.",
        default=False
    )
    operationParams = serializers.DictField(
        help_text="Input parameters of the LCM operation. This attribute " +
        "shall be formatted according to the request data type of the " +
        "related LCM operation. The following mapping between operationType and the " +
        "data type of this attribute shall apply: " +
        "1. INSTANTIATE: InstantiateVnfRequest" +
        "2. SCALE: ScaleVnfRequest " +
        "3. SCALE_TO_LEVEL: ScaleVnfToLevelRequest " +
        "4. CHANGE_FLAVOUR: ChangeVnfFlavourRequest " +
        "5. OPERATE: OperateVnfRequest " +
        "6. HEAL: HealVnfRequest " +
        "7. CHANGE_EXT_CONN: ChangeExtVnfConnectivityRequest " +
        "8. TERMINATE: TerminateVnfRequest " +
        "9. MODIFY_INFO: VnfInfoModifications",
        required=True,
        allow_null=False
    )
    isCancelPending = serializers.BooleanField(
        help_text="If the VNF LCM operation occurrence is in 'STARTING'" +
        "'PROCESSING' or 'ROLLING_BACK' state and the operation is being" +
        " cancelled, this attribute shall be set to True. Otherwise, " +
        " it shall be set to False.",
        required=True
    )
    cancelMode = serializers.CharField(
        help_text="The mode of an ongoing cancellation. Shall be present " +
        "when isCancelPending=true, and shall be None otherwise.",
        allow_null=True,
        required=False
    )
    error = ProblemDetailsSerializer(
        help_text="If 'operationState' is 'FAILED_TEMP' or 'FAILED' or " +
        "'PROCESSING' or 'ROLLING_BACK' and previous value of 'operationState' " +
        "was 'FAILED_TEMP'  this attribute shall be present ",
        allow_null=True,
        required=False
    )
    resourceChanges = ResourceChangesSerializer(
        help_text="It contains information about the cumulative changes " +
        "to virtualised resources that were performed so far by the LCM " +
        "operation since its start, if applicable.",
        required=False,
        allow_null=True)
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
    _links = LcmOpLinkSerializer(
        help_text="Links to resources related to this resource.",
        required=True)
