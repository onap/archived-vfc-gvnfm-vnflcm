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


class StorageResourceSerializer(serializers.Serializer):
    resourceId = serializers.CharField(help_text="resourceId", required=True)
    vimId = serializers.CharField(help_text="vimId", required=True)


class virtualStorageResourceInfoSerializer(serializers.Serializer):
    virtualStorageInstanceId = serializers.CharField(help_text="virtualStorageInstanceId", required=True)
    storageResource = StorageResourceSerializer(help_text="storageResource", required=True)


class virtualLinkResourceInfoSerializer(serializers.Serializer):
    pass


class vnfcResourceInfoSerializer(serializers.Serializer):
    pass


class accessInfoSerializer(serializers.Serializer):
    tenant = serializers.CharField(help_text="tenant", required=True)
    username = serializers.CharField(help_text="username", required=True)
    password = serializers.CharField(help_text="password", required=True)


class InterfaceInfoSerializer(serializers.Serializer):
    vimType = serializers.CharField(help_text="vimType", required=True)
    apiVersion = serializers.CharField(help_text="apiVersion", required=True)
    protocolType = serializers.ChoiceField(help_text="protocolType", choices=['http', 'https'], required=True)


class vimInfoSerializer(serializers.Serializer):
    vimInfoId = serializers.CharField(help_text="vimInfoId", required=True)
    vimId = serializers.CharField(help_text="vimId", required=True)
    interfaceEndpoint = serializers.CharField(help_text="interfaceEndpoint", required=True)
    interfaceInfo = InterfaceInfoSerializer(help_text="vimInfoId", required=True)
    accessInfo = accessInfoSerializer(help_text="accessInfo", required=True)


class monitoringParametersSerializer(serializers.Serializer):
    pass


class linkPortsSerializer(serializers.Serializer):
    resourceId = serializers.CharField(help_text="resourceId", required=True)
    vimId = serializers.CharField(help_text="vimId", required=False)


class resourceHandleSerializer(serializers.Serializer):
    resourceId = serializers.CharField(help_text="resourceId", required=True)
    vimId = serializers.CharField(help_text="vimId", required=False)
    resourceProviderId = serializers.CharField(help_text="resourceProviderId", required=False)


class ExtVirtualLinkInfoSerializer(serializers.Serializer):
    extVirtualLinkId = serializers.CharField(help_text="extVirtualLinkId", required=True)
    resourceHandle = resourceHandleSerializer(help_text="iPAddress", required=True)
    linkPorts = linkPortsSerializer(help_text="iPAddress", many=True, allow_null=True)


class l3AddressDataSerializer(serializers.Serializer):
    iPAddressType = serializers.ChoiceField(help_text="iPAddressType", choices=['IPv4', 'IPv6'], required=True)
    iPAddress = serializers.CharField(help_text="iPAddress", required=True)


class NetworkAddressSerializer(serializers.Serializer):
    addressType = serializers.ChoiceField(help_text="addressType", choices=['MAC', 'IP'], required=True)
    l2AddressData = serializers.CharField(help_text="l2AddressData", required=False)
    l3AddressData = l3AddressDataSerializer(help_text="addresses", required=False)


class extCpInfoSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(help_text="cpInstanceId", required=True)
    cpdId = serializers.IntegerField(help_text="cpdId", required=True)
    addresses = NetworkAddressSerializer(help_text="addresses", many=True, allow_null=True)


class ScaleInfoSerializer(serializers.Serializer):
    aspectId = serializers.CharField(help_text="aspectId", required=True)
    scaleLevel = serializers.IntegerField(help_text="scaleLevel", required=True)


class instantiatedVnfInfoSerializer(serializers.Serializer):
    flavourId = serializers.CharField(help_text="flavour Id", required=True, allow_null=True)
    vnfState = serializers.ChoiceField(help_text="vnf State", choices=['STARTED', 'STOPPED'], required=True, allow_null=True)
    scaleStatus = ScaleInfoSerializer(help_text="scaleStatus", many=True)
    extCpInfo = extCpInfoSerializer(help_text="extCpInfo", many=True)
    extVirtualLink = ExtVirtualLinkInfoSerializer(help_text="extVirtualLink", many=True)
    monitoringParameters = monitoringParametersSerializer(help_text="monitoringParameters", allow_null=True)
    vimInfo = vimInfoSerializer(help_text="vimInfo", many=True)
    vnfcResourceInfo = vnfcResourceInfoSerializer(help_text="vnfcResourceInfo", many=True)
    virtualLinkResourceInfo = virtualLinkResourceInfoSerializer(help_text="virtualLinkResourceInfo", many=True)
    virtualStorageResourceInfo = virtualStorageResourceInfoSerializer(help_text="virtualStorageResourceInfo", many=True)
    pass


class VnfInfoSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="vnf Instance Id", required=True)
    vnfInstanceName = serializers.CharField(help_text="vnf Instance Name", required=True)
    onboardedVnfPkgInfoId = serializers.CharField(help_text="onboarded Vnf Pkg Info Id", required=False,
                                                  allow_null=True)
    vnfdVersion = serializers.CharField(help_text="vnfd Version", required=False, allow_null=True)
    vnfProvider = serializers.CharField(help_text="vnf Provider", required=False, allow_null=True)
    instantiatedVnfInfo = instantiatedVnfInfoSerializer(help_text="instantiatedVnfInfo", required=True)


class VnfsInfoSerializer(serializers.ListSerializer):
    child = VnfInfoSerializer()
