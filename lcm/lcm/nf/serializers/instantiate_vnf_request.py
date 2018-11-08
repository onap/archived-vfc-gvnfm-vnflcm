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

from ext_virtual_link_data import ExtVirtualLinkDataSerizlizer
from ext_managed_virtual_link_data import ExtManagedVirtualLinkDataSerizlizer
from vim_connection_info import VimConnectionInfoSerializer


class InstantiateVnfRequestSerializer(serializers.Serializer):
    flavourId = serializers.CharField(
        help_text="Identifier of the VNF deployment flavour to be instantiated.",
        max_length=255,
        required=True,
        allow_null=True)
    instantiationLevelId = serializers.CharField(
        help_text="Identifier of the instantiation level of the deployment flavour to be instantiated. \
        If not present, the default instantiation level as declared in the VNFD is instantiated.",
        max_length=255,
        required=False,
        allow_null=True)
    extVirtualLinks = ExtVirtualLinkDataSerizlizer(
        help_text="Information about external VLs to connect the VNF to.",
        many=True,
        required=False,
        allow_null=True)
    extManagedVirtualLinks = ExtManagedVirtualLinkDataSerizlizer(
        help_text="Information about internal VLs that are managed by the NFVO.",
        many=True,
        required=False,
        allow_null=True)
    vimConnectionInfo = VimConnectionInfoSerializer(
        help_text="Information about VIM connections to be used for managing the resources for the VNF instance, \
        or refer to external / externally-managed virtual links.",
        many=True,
        required=False,
        allow_null=True)
    localizationLanguage = serializers.CharField(
        help_text="Localization language of the VNF to be instantiated. \
        The value shall comply with the format defined in IETF RFC 5646.",
        max_length=255,
        required=False,
        allow_null=True)
    additionalParams = serializers.JSONField(
        help_text="Additional input parameters for the instantiation process, \
        specific to the VNF being instantiated, \
        as declared in the VNFD as part of InstantiateVnfOpConfig.",
        # child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
