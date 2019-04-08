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


class ChangeExtVnfConnectivityRequestSerializer(serializers.Serializer):
    extVirtualLinks = ExtVirtualLinkDataSerizlizer(
        help_text="Information about external VLs to change (e.g. connect the VNF to).",
        many=True,
        required=True,
        allow_null=False
    )
    vimConnectionInfo = VimConnectionInfoSerializer(
        help_text="Information about VIM connections to be used for " +
        "managing the resources for the VNF instance, " +
        "or refer to external virtual links." +
        "This attribute shall only be supported and may be present " +
        "if VNF-related resource management in direct mode is applicable.",
        many=True,
        required=False,
        allow_null=True
    )
    additionalParams = serializers.DictField(
        help_text="Additional parameters passed by the NFVO as input to the process, " +
        "specific to the VNF of which the external connectivity is changed, " +
        "as declared in the VNFD as part of 'ChangeExtVnfConnectivityOpConfig'.",
        required=False,
        allow_null=True
    )
