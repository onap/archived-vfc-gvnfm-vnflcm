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

from vim_connection_info import VimConnectionInfoSerializer
from instantiated_vnf_info import InstantiatedVnfInfoSerializer
from _links import _LinksSerializer


class VnfInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the VNF instance.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    vnfInstanceName = serializers.CharField(
        help_text="Name of the VNF instance. \
        This attribute can be modified with the PATCH method.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfInstanceDescription = serializers.CharField(
        help_text="Human-readable description of the VNF instance. \
        This attribute can be modified with the PATCH method.",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfdId = serializers.CharField(
        help_text="Identifier of the VNFD on which the VNF instance is based.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfProvider = serializers.CharField(
        help_text="Provider of the VNF and the VNFD. \
        The value is copied from the VNFD. ",
        max_length=255,
        required=True,
        allow_null=True,
        allow_blank=False)
    vnfProductName = serializers.CharField(
        help_text="Name to identify the VNF Product. \
        The value is copied from the VNFD.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfSoftwareVersion = serializers.CharField(
        help_text="Software version of the VNF. \
        The value is copied from the VNFD.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfdVersion = serializers.CharField(
        help_text="Identifies the version of the VNFD. \
        The value is copied from the VNFD.",
        max_length=255,
        required=True,
        allow_null=True,
        allow_blank=False)
    vnfPkgId = serializers.CharField(
        help_text="Identifier of information held by the NFVO about the specific VNF package on which the VNF is based. \
        This attribute can be modified with the PATCH method.",
        max_length=255,
        required=True,
        allow_null=True,
        allow_blank=False)
    vnfConfigurableProperties = serializers.DictField(
        help_text="Current values of the configurable properties of the VNF instance. \
        Configurable properties referred in this attribute are declared in the VNFD",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True,)
    vimConnectionInfo = VimConnectionInfoSerializer(
        help_text="Information about VIM connections to be used for managing the resources for the VNF instance. \
        This attribute can be modified with the PATCH method.",
        required=False,
        allow_null=True)
    instantiationState = serializers.ChoiceField(
        help_text="The instantiation state of the VNF.",
        choices=["NOT_INSTANTIATED", "INSTANTIATED"],
        required=False,
        allow_null=True,
        allow_blank=True)
    instantiatedVnfInfo = InstantiatedVnfInfoSerializer(
        help_text="Information specific to an instantiated VNF instance. \
        This attribute shall be present if the instantiateState attribute value is INSTANTIATED",
        required=False,
        allow_null=True)
    metadata = serializers.DictField(
        help_text="Additional VNF-specific metadata describing the VNF instance.\
        This attribute can be modified with the PATCH method.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
    extensions = serializers.DictField(
        help_text="VNF-specific attributes that affect the lifecycle management of this VNF instance by the VNFM, or the lifecycle management scripts. \
        This attribute can be modified with the PATCH method.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
    _links = _LinksSerializer(
        help_text="Links to resources related to this resource.",
        required=False,
        allow_null=False)
