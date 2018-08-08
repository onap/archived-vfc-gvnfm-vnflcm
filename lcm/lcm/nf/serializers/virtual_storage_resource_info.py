# Copyright 2018 ZTE Corporation.
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


class VirtualStorageResourceInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this VirtualStorageResourceInfo instance.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    virtualStorageDescId = serializers.CharField(
        help_text="Identifier of the VirtualStorageDesc in the VNFD.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    storageResource = ResourceHandleSerializer(
        help_text="Reference to the VirtualStorage resource.",
        required=True,
        allow_null=False)
    reservationId = serializers.CharField(
        help_text="The reservation identifier applicable to the resource.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    metadata = serializers.DictField(
        help_text="Metadata about this resource.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
