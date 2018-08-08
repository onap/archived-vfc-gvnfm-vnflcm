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

from cp_protocol_info import CpProtocolInfoSerializer


class ExtCpInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the external CP instance and the related information instance.",
        max_length=255,
        required=True,
        allow_null=True,
        allow_blank=False)
    cpdId = serializers.CharField(
        help_text="Identifier of the external CPD, VnfExtCpd, in the VNFD.",
        max_length=255,
        required=True,
        allow_null=True,
        allow_blank=False)
    cpProtocolInfo = CpProtocolInfoSerializer(
        help_text="Network protocol information for this CP.",
        many=True,
        required=False,
        allow_null=True)
    extLinkPortId = serializers.CharField(
        help_text="Identifier of the extLinkPortInfo structure inside the extVirtualLinkInfo structure.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
