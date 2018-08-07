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


class ExtlinkPortsSerializer(serializers.Serializer):
    resourceId = serializers.CharField(
        help_text="resourceId",
        required=True,
        max_length=255,
        allow_null=True)
    vimId = serializers.CharField(
        help_text="vimId",
        required=False,
        max_length=255,
        allow_null=True)