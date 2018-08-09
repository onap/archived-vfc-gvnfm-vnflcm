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


class TerminateVnfRequestSerializer(serializers.Serializer):
    terminationType = serializers.ChoiceField(
        help_text="terminationType: Indicates whether forceful or graceful termination is requested.",
        choices=["FORCEFUL", "GRACEFUL"],
        required=True,
        allow_null=True)
    gracefulTerminationTimeout = serializers.IntegerField(
        help_text="This attribute is only applicable in case of graceful termination",
        default=120,
        required=False)
