# Copyright (C) 2018 Verizon. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rest_framework import serializers


class ScaleVnfRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        help_text="Indicates the type of the scale operation requested.",
        choices=["SCALE_OUT", "SCALE_IN"],
        required=True,
        allow_null=False,
        allow_blank=False)
    aspectId = serializers.CharField(
        help_text="Identifier of the scaling aspect.",
        required=False,
        allow_blank=True,
        allow_null=True)
    numberOfSteps = serializers.IntegerField(
        help_text="Number of scaling steps to be executed as part of this Scale VNF operation. " +
        "It shall be a positive number and the default value shall be 1.",
        default=1,
        required=False)
    additionalParams = serializers.DictField(
        help_text="Additional parameters passed by the NFVO as input to the scaling process, " +
        "specific to the VNF being scaled, " +
        "as declared in the VNFD as part of 'ScaleVnfOpConfig'.",
        required=False,
        allow_null=True)
