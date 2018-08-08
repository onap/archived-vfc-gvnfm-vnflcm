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


class CpProtocolInfoSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(
        help_text="The identifier of layer(s) and protocol(s) associated to the network address information.",
        choices=["IP_OVER_ETHERNET"],
        required=True,
        allow_null=False,
        allow_blank=False)
    ipOverEthernet = serializers.DictField(
        help_text="IP addresses over Ethernet to assign to the extCP instance.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True,)
