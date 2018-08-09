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

from ip_over_ethernet_address_data import IpOverEthernetAddressDataSerializer


class CpProtocolDataSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(
        help_text="Identifier of layer(s) and protocol(s).",
        choices=["IP_OVER_ETHERNET"],
        required=True,
        allow_null=False,
        allow_blank=False)
    ipOverEthernet = IpOverEthernetAddressDataSerializer(
        help_text="Network address data for IP over Ethernet to assign to the extCP instance. \
        Shall be present if layerProtocol is equal to IP_OVER_ETHERNET, \
        and shall be absent otherwise.",
        required=False,
        allow_null=True,)
