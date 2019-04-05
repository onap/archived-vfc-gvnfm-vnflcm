# Copyright (c) 2019, CMCC Technologies Co., Ltd.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rest_framework import serializers
from .scale_info import ScaleInfoSerializer


class ScaleVnfToLevelRequestSerializer(serializers.Serializer):
    instantiationLevelId = serializers.CharField(
        help_text="Identifier of the target instantiation level of" +
        "the current deployment flavour to which the VNF is requested to be scaled.",
        required=False,
        allow_null=True)
    scaleInfo = ScaleInfoSerializer(
        help_text="For each scaling aspect of the current deployment flavour," +
        "indicates the target scale level to which the VNF is to be scaled.",
        many=True)
    additionalParams = serializers.DictField(
        help_text="Additional parameters passed by the NFVO as input to the scaling process",
        required=False,
        allow_null=True,
        child=serializers.CharField(
            help_text="KeyValue Pairs",
            allow_blank=True))


class NfOperateJobSerializer(serializers.Serializer):
    jobId = serializers.CharField(
        help_text="ID of NF operate job",
        required=True)
