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

from resource import ResourceSerializer


class VnfcResourceInfoSerializer(serializers.Serializer):
    vnfcInstanceId = serializers.CharField(
        help_text="vnfcInstanceId",
        required=False,
        max_length=255,
        allow_null=True)
    vduId = serializers.CharField(
        help_text="vduId",
        required=False, max_length=255, allow_null=True)
    storageResourceIds = serializers.CharField(
        help_text="storageResourceIds",
        required=False,
        max_length=255,
        allow_null=True)
    computeResource = ResourceSerializer(
        help_text="computeResource",
        required=False,
        allow_null=True)