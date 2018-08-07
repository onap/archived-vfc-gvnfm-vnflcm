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
from vnf_link_port_info import VnfLinkPortInfoSerializer


class VirtualLinkResourceInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this VnfVirtualLinkResourceInfo instance.",
        required=False,
        max_length=255,
        allow_null=True)
    virtualLinkDescId = serializers.CharField(
        help_text="virtualLinkDescId",
        required=False,
        max_length=255,
        allow_null=True)
    networkResource = ResourceHandleSerializer(
        help_text="networkResource",
        required=False,
        allow_null=True)
    reservationId = serializers.CharField(
        help_text="The reservation identifier applicable to the resource.",
        required=False,
        max_length=255,
        allow_null=True)
    vnfLinkPorts = VnfLinkPortInfoSerializer(
        help_text="Links ports of this VL.",
        required=False,
        max_length=255,
        allow_null=True)
    metadata = serializers.DictField(
        help_text="Metadata about this resource.",
        required=False,
        allow_null=True)
