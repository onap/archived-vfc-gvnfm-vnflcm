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

from link import LinkSerializer

class _LinksSerializer(serializers.Serializer):
    href = LinkSerializer(
        help_text="URI of this resource.",
        required=True,
        allow_null=False)
    indicators = LinkSerializer(
        help_text="Indicators related to this VNF instance.",
        required=False,
        allow_null=True)
    instantiate = LinkSerializer(
        help_text="Link to the instantiate task resource.",
        required=False,
        allow_null=True)
    termiante = LinkSerializer(
        help_text="Link to the terminate task resource.",
        required=False,
        allow_null=True)
    scale = LinkSerializer(
        help_text="Link to the scale task resource.",
        required=False,
        allow_null=True)
    scaleToLevel = LinkSerializer(
        help_text="Link to the scale_to_level task resource.",
        required=False,
        allow_null=True)
    changeFlavour = LinkSerializer(
        help_text="Link to the change_flavour task resource.",
        required=False,
        allow_null=True)
    heal = LinkSerializer(
        help_text="Link to the heal task resource.",
        required=False,
        allow_null=True)
    operate = LinkSerializer(
        help_text="Link to the operate task resource.",
        required=False,
        allow_null=True)
    changeExtConn = LinkSerializer(
        help_text="Link to the change_ext_conn task resource.",
        required=False,
        allow_null=True)