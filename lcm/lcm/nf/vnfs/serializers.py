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


class CreateVnfReqSerializer(serializers.Serializer):
    vnfdId = serializers.CharField(help_text="vnfd Id", required=True)
    vnfInstanceName = serializers.CharField(help_text="vnf Instance Name", required=True)
    vnfInstanceDescription = serializers.CharField(help_text="vnf Instance Description", required=False, allow_null=True)


class CreateVnfRespSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="vnf Instance Id", required=True)


class virtualStorageResourceInfoSerializer(serializers.Serializer):
    pass


class virtualLinkResourceInfoSerializer(serializers.Serializer):
    pass


class vnfcResourceInfoSerializer(serializers.Serializer):
    pass


class vimInfoSerializer(serializers.Serializer):
    pass


class monitoringParametersSerializer(serializers.Serializer):
    pass


class ExtVirtualLinkInfoSerializer(serializers.Serializer):
    pass


class extCpInfoSerializer(serializers.Serializer):
    pass


class ScaleInfoSerializer(serializers.Serializer):
    pass


class instantiatedVnfInfoSerializer(serializers.Serializer):
    flavourId = serializers.CharField(help_text="flavour Id", required=True)
    vnfState = serializers.ChoiceField(help_text="vnf State", choices=['STARTED', 'STOPPED'], required=True)
    scaleStatus = ScaleInfoSerializer(help_text="scaleStatus", many=True)
    extCpInfo = extCpInfoSerializer(help_text="extCpInfo", many=True)
    extVirtualLink = ExtVirtualLinkInfoSerializer(help_text="extVirtualLink", many=True)
    monitoringParameters = monitoringParametersSerializer(help_text="monitoringParameters", many=True, allow_null=True)
    vimInfo = vimInfoSerializer(help_text="vimInfo", many=True)
    vnfcResourceInfo = vnfcResourceInfoSerializer(help_text="vnfcResourceInfo", many=True)
    virtualLinkResourceInfo = virtualLinkResourceInfoSerializer(help_text="virtualLinkResourceInfo", many=True)
    virtualStorageResourceInfo = virtualStorageResourceInfoSerializer(help_text="virtualStorageResourceInfo", many=True)
    pass


class VnfsInfoSerializer(serializers.ListSerializer):
    vnfInstanceId = serializers.CharField(help_text="vnf Instance Id", required=True)
    vnfInstanceName = serializers.CharField(help_text="vnf Instance Name", required=True)
    onboardedVnfPkgInfoId = serializers.CharField(help_text="onboarded Vnf Pkg Info Id", required=False,
                                                  allow_null=True)
    vnfdVersion = serializers.CharField(help_text="vnfd Version", required=False, allow_null=True)
    vnfProvider = serializers.CharField(help_text="vnf Provider", required=False, allow_null=True)
    instantiatedVnfInfo = instantiatedVnfInfoSerializer(help_text="instantiatedVnfInfo", required=True)
