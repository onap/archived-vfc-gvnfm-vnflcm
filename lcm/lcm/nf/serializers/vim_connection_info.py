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


class VimConnectionInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="The identifier of the VIM Connection. This identifier is managed by the NFVO.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    vimId = serializers.CharField(
        help_text="The identifier of the VIM instance. This identifier is managed by the NFVO.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vimType = serializers.CharField(
        help_text="Discriminator for the different types of the VIM information.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
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
        help_text="VIM type specific additional information. \
        The applicable structure, and whether or not this attribute is available, is dependent on the content of vimType.",
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_null=True)