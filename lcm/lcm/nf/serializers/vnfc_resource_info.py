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
from vnfc_cp_info import VnfcCpInfoSerializer


class VnfcResourceInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this VnfcResourceInfo instance.",
        max_length=255,
        required=False,
        allow_null=False)
    vduId = serializers.CharField(
        help_text="Reference to the applicable VDU in the VNFD.",
        max_length=255,
        required=False,
        allow_null=False)
    computeResource = ResourceHandleSerializer(
        help_text="Reference to the VirtualCompute resource.",
        required=True,
        allow_null=False)
    storageResourceIds = serializers.CharField(
        help_text="References to the VirtualStorage resources. \
        The value refers to a VirtualStorageResourceInfo item in the VnfInstance.",
        max_length=255,
        many=True,
        required=False,
        allow_null=True,
        allow_blank=True)
    reservationId = serializers.CharField(
        help_text="The reservation identifier applicable to the resource.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfcCpInfo = VnfcCpInfoSerializer(
        help_text="CPs of the VNFC instance. \
        Shall be present when that particular CP of the VNFC instance is associated to an external CP of the VNF instance.",
        many=True,
        required=False,
        allow_null=True)
    metadata = serializers.DictField(
        help_text="Metadata about this resource.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
