# Copyright (C) 2018 Verizon. All Rights Reserved.
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


class VnfInfoModificationsSerializer(serializers.Serializer):
    vnfInstanceName = serializers.CharField(
        help_text="If present, this attribute signals modifications of the " +
        "'vnfInstanceName' attribute in 'VnfInstance'",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfInstanceDescription = serializers.CharField(
        help_text="If present, this attribute signals modifications of the " +
        "'vnfInstanceDescription' attribute in 'VnfInstance'",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfdId = serializers.CharField(
        help_text="If present, this attribute signals modifications of the " +
        "'vnfdId' attribute in 'VnfInstance'",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfProvider = serializers.CharField(
        help_text="If present, this attribute signals modifications of the " +
        "'vnfProvider'  attribute in 'VnfInstance'",
        max_length=255,
        required=False,
        allow_null=True)
    vnfProductName = serializers.CharField(
        help_text="If present, this attribute signals modifications of the " +
        "'vnfProductName' attribute in 'vnfInstance'",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfSoftwareVersion = serializers.CharField(
        help_text="If present, this attribute signals modifications of the " +
        "'vnfSoftwareVersion' attribute in 'VnfInstance'.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfdVersion = serializers.CharField(
        help_text="If present, this attribute signals modifications of the " +
        "'vnfdVersion' attribute in 'VnfInstance'. ",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=False)
    vnfPkgId = serializers.CharField(
        help_text="If present, this attribute signals modifications of the " +
        "'vnfPkgId' attribute in 'VnfInstance'.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=False)
    vnfConfigurableProperties = serializers.DictField(
        help_text="If present, this attribute signals modifications of the " +
        "'vnfConfigurableProperties'  attribute in 'VnfInstance'. ",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True,)
    vimConnectionInfo = VimConnectionInfoSerializer(
        help_text="If present, this attribute signals modifications of certain" +
        "entries in the 'vimConnectionInfo'",
        required=False,
        many=True,
        allow_null=True)
    metadata = serializers.DictField(
        help_text="If present, this attribute signals modifications of certain" +
        "'metadata' attribute in 'vnfInstance'.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
    extensions = serializers.DictField(
        help_text="If present, this attribute signals modifications of certain" +
        "'extensions' attribute in 'vnfInstance'.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
