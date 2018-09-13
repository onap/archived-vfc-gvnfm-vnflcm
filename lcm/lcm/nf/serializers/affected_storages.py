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
from lcm.nf.const import CHANGE_TYPE

CHANGE_TYPES = [
    CHANGE_TYPE.ADDED,
    CHANGE_TYPE.REMOVED,
    CHANGE_TYPE.MODIFIED,
    CHANGE_TYPE.TEMPORARY
]


class AffectedStoragesSerializer(serializers.Serializer):
    id = serializers.UUIDField(
        help_text="Identifier of the Storage instance, identifying the " +
        "applicable 'virtualStorageResourceInfo' entry in the 'VnfInstance' data type",
        required=True
    )
    virtualStorageDescId = serializers.UUIDField(
        help_text="Identifier of the related VirtualStorage descriptor " +
        "in the VNFD. ",
        required=True
    )
    changeType = serializers.ChoiceField(
        help_text="Signals the type of change",
        required=True,
        choices=CHANGE_TYPES
    )
    metadata = serializers.DictField(
        help_text="Metadata about this resource. ",
        required=False,
        allow_null=True)
    storageResource = ResourceHandleSerializer(
        help_text="Reference to the VirtualStorage resource.",
        required=True,
        allow_null=False)
