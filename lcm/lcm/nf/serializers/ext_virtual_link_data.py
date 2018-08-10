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

from vnf_ext_cp_data import VnfExtCpDataSerializer
from ext_link_port_data import ExtLinkPortDataSerializer


class ExtVirtualLinkDataSerizlizer(serializers.Serializer):
    id = serializers.CharField(
        help_text="The identifier of the external VL instance. \
        The identifier is assigned by the NFV-MANO entity that manages this VL instance.",
        max_length=255,
        required=True,
        allow_null=True)
    vimConnectionId = serializers.CharField(
        help_text="Identifier of the VIM connection to manage this resource. \
        This attribute shall only be supported and present if VNF-related resource management in direct mode is applicable.",
        max_length=255,
        required=False,
        allow_null=True)
    resourceProviderId = serializers.CharField(
        help_text="Identifies the entity responsible for the management of this resource. \
        This attribute shall only be supported and present if VNF-related resource management in indirect mode is applicable.",
        max_length=255,
        required=False,
        allow_null=True)
    resourceId = serializers.CharField(
        help_text="The identifier of the resource in the scope of the VIM or the resource provider.",
        max_length=255,
        required=True,
        allow_null=False)
    resourceSubnetId = serializers.CharField(
        help_text="Subnet defined by the identifier of the subnet resource in the VIM.",
        max_length=255,
        required=True,
        allow_null=False)
    extCps = VnfExtCpDataSerializer(
        help_text="External CPs of the VNF to be connected to this external VL.",
        many=True,
        required=True,
        allow_null=False)
    extLinkPorts = ExtLinkPortDataSerializer(
        help_text="Externally provided link ports to be used to connect external connection points to this external VL. \
        If this attribute is not present, the VNFM shall create the link port on the external VL.",
        many=True,
        required=False,
        allow_null=True)
