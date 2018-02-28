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


class VimInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="The identifier of the VIM Connection. This identifier is managed by the NFVO.",
        required=False,
        max_length=255,
        allow_null=True)
    vimId = serializers.CharField(
        help_text="The identifier of the VIM instance. This identifier is managed by the NFVO.",
        required=False,
        max_length=255,
        allow_null=True)
    vimType = serializers.CharField(
        help_text="Discriminator for the different types of the VIM information.",
        required=False,
        max_length=255,
        allow_null=True)
    interfaceInfo = serializers.DictField(
        help_text="Information about the interface or interfaces to the VIM",
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_null=True)
    accessInfo = serializers.DictField(
        help_text="Authentication credentials for accessing the VIM, and other access-related information",
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_null=True)
    extra = serializers.DictField(
        help_text="VIM type specific additional information.",
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_null=True)


class VnfInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the VNF instance",
        required=True)
    vnfInstanceName = serializers.CharField(
        help_text="Name of the VNF instance.",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfInstanceDescription = serializers.CharField(
        help_text="Human-readable description of the VNF instance.",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfdId = serializers.CharField(
        help_text="Identifier of the VNFD on which the VNF instance is based.",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfProvider = serializers.CharField(
        help_text="Provider of the VNF and the VNFD. The value is copied from the VNFD.",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfProductName = serializers.CharField(
        help_text="Name to identify the VNF Product. The value is copied from the VNFD.",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfSoftwareVersion = serializers.CharField(
        help_text="Software version of the VNF. The value is copied from the VNFD.",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfdVersion = serializers.CharField(
        help_text="Identifies the version of the VNFD. The value is copied from the VNFD.",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfPkgId = serializers.CharField(
        help_text="Identifier of information held by the NFVO about the specific VNF package on which the VNF is based.",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfConfigurableProperties = serializers.DictField(
        help_text="Current values of the configurable properties of the VNF instance.",
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_null=True)
    vimConnectionInfo = VimInfoSerializer(
        help_text="vim",
        required=False,
        allow_null=True)
    instantiationState = serializers.ChoiceField(
        help_text="The instantiation state of the VNF.",
        choices=["NOT_INSTANTIATED", "INSTANTIATED"],
        required=False,
        allow_null=True)
