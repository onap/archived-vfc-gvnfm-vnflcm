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

from cp_protocol_data import CpProtocolDataSerializer


class VnfExtCpConfigSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(
        help_text="Identifier of the external CP instance to which this set of configuration parameters is requested to be applied. \
        Shall be present if this instance has already been created.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    linkPortId = serializers.CharField(
        help_text="Identifier of a pre-configured link port to which the external CP will be associated.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    cpProtocolData = CpProtocolDataSerializer(
        help_text="Parameters for configuring the network protocols on the link port that connects the CP to a VL.",
        many=True,
        required=False,
        allow_null=True)
