# Copyright (C) 2019 ZTE. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rest_framework import serializers
from .ext_virtual_link_data import ExtVirtualLinkDataSerizlizer
from .vim_connection_info import VimConnectionInfoSerializer
from .ext_managed_virtual_link_data import ExtManagedVirtualLinkDataSerizlizer


class ChangeVnfFlavourRequestSerializer(serializers.Serializer):
    newFlavourId = serializers.CharField(
        help_text="Identifier of the VNF deployment flavour to be instantiated.",
        required=True,
        allow_null=False,
        allow_blank=False
    )
    instantiationLevelId = serializers.CharField(
        help_text="Identifier of the instantiation level of the deployment flavour to be instantiated. " +
        "If not present, the default instantiation level as declared in the VNFD is instantiated.",
        required=False,
        allow_blank=True,
        allow_null=True
    )
    extVirtualLinks = ExtVirtualLinkDataSerizlizer(
        help_text="Information about external VLs to connect the VNF to.",
        many=True,
        required=False,
        allow_null=True
    )
    extManagedVirtualLinks = ExtManagedVirtualLinkDataSerizlizer(
        help_text="Information about internal VLs that are managed by the NFVO.",
        many=True,
        required=False,
        allow_null=True
    )
    vimConnectionInfo = VimConnectionInfoSerializer(
        help_text="Information about VIM connections to be used for managing " +
        "the resources for the VNF instance, " +
        "or refer to external / externally-managed virtual links." +
        "This attribute shall only be supported and may be present if VNF-related " +
        "resource management in direct mode is applicable.",
        many=True,
        required=False,
        allow_null=True
    )
    additionalParams = serializers.DictField(
        help_text="Additional input parameters for the flavour change process, " +
        "specific to the VNF being modified, " +
        "as declared in the VNFD as part of 'ChangeVnfFlavourOpConfig'.",
        required=False,
        allow_null=True
    )
