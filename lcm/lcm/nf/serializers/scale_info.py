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


class ScaleInfoSerializer(serializers.Serializer):
    aspectId = serializers.CharField(
        help_text="Identifier of the scaling aspect.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    scaleLevel = serializers.IntegerField(
        help_text="Indicates the scale level. \
        The minimum value shall be 0 and the maximum value shall be <= maxScaleLevel as described in the VNFD.",
        required=True,
        allow_null=False)
