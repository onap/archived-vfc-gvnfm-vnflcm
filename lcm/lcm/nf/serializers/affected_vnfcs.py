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

from resource_handle import ResourceHandleSerializer

CHANGE_TYPES = [
    "ADDED",
    "REMOVED",
    "MODIFIED",
    "TEMPORARY"
]


class AffectedVnfcsSerializer(serializers.Serializer):
    id = serializers.UUIDField(
        help_text="Identifier of the Vnfc instance, identifying the " +
        "applicable 'vnfcResourceInfo' entry in the 'VnfInstance' data type",
        required=True
    )
    vduId = serializers.UUIDField(
        help_text="Identifier of the related VDU in the VNFD.",
        required=True
    )
    changeType = serializers.ChoiceField(
        help_text="Signals the type of change",
        required=True,
        choices=CHANGE_TYPES
    )
    affectedVnfcCpIds = serializers.ListField(
        help_text="Identifiers of CP(s) of the VNFC instance that " +
        "were affected by the change",
        required=False,
        child=serializers.UUIDField(required=True)
    )
    addedStorageResourceIds = serializers.ListField(
        help_text="References to VirtualStorage resources that " +
        "have been added",
        required=False,
        child=serializers.UUIDField()
    )
    removedStorageResourceIds = serializers.ListField(
        help_text="References to VirtualStorage resources that " +
        "have been removed.",
        required=False,
        child=serializers.UUIDField()
    )
    metadata = serializers.DictField(
        help_text="Metadata about this resource. ",
        required=False,
        allow_null=True)
    computeResource = ResourceHandleSerializer(
        help_text="Reference to the VirtualCompute resource.",
        required=True,
        allow_null=False)
