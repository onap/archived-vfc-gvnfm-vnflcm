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


class ExtManagedVirtualLinkInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the externally-managed internal VL and the related externally-managed VL information instance.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    vnfVirtualLinkDescId = serializers.CharField(
        help_text="Identifier of the VNF Virtual Link Descriptor (VLD) in the VNFD.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    networkResource = ResourceHandleSerializer(
        help_text="ResourceHandle,reference to the VirtualNetwork resource.",
        required=True,
        allow_null=False)
    vnfLinkPorts = VnfLinkPortInfoSerializer(
        help_text="VnfLinkPortInfo, Link ports of this VL.",
        many=True,
        required=False,
        allow_null=True)
