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
    vnfdId = serializers.CharField(
        help_text="Identifier that identifies the VNFD which defines the VNF instance to be created.",
        max_length=255,
        required=True,
        allow_null=True)
    vnfInstanceName = serializers.CharField(
        help_text="Human-readable name of the VNF instance to be created.",
        max_length=255,
        required=True,
        allow_null=False)
    vnfInstanceDescription = serializers.CharField(
        help_text="Human-readable description of the VNF instance to be created.",
        max_length=255,
        required=False,
        allow_null=True)


class CreateVnfRespSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(
        help_text="Identifier of the VNF instance",
        required=True,
        max_length=255,
        allow_null=True)


class ResourceSerializer(serializers.Serializer):
    resourceId = serializers.CharField(
        help_text="resourceId",
        required=True,
        max_length=255,
        allow_null=True)
    vimId = serializers.CharField(
        help_text="vimId",
        required=True,
        max_length=255,
        allow_null=True)


class VirtualStorageResourceInfoSerializer(serializers.Serializer):
    virtualStorageInstanceId = serializers.CharField(
        help_text="virtualStorageInstanceId",
        required=False,
        allow_null=True,
        max_length=255)
    virtualStorageDescId = serializers.CharField(
        help_text="virtualStorageDescId",
        required=False,
        max_length=255,
        allow_null=True)
    storageResource = ResourceSerializer(
        help_text="storageResource",
        required=False,
        allow_null=True)


class VirtualLinkResourceInfoSerializer(serializers.Serializer):
    virtualLinkInstanceId = serializers.CharField(
        help_text="virtualLinkInstanceId",
        required=False,
        max_length=255,
        allow_null=True)
    virtualLinkDescId = serializers.CharField(
        help_text="virtualLinkDescId",
        required=False,
        max_length=255,
        allow_null=True)
    networkResource = ResourceSerializer(
        help_text="networkResource",
        required=False,
        allow_null=True)


class VnfcResourceInfoSerializer(serializers.Serializer):
    vnfcInstanceId = serializers.CharField(
        help_text="vnfcInstanceId",
        required=False,
        max_length=255,
        allow_null=True)
    vduId = serializers.CharField(
        help_text="vduId",
        required=False, max_length=255, allow_null=True)
    storageResourceIds = serializers.CharField(
        help_text="storageResourceIds",
        required=False,
        max_length=255,
        allow_null=True)
    computeResource = ResourceSerializer(
        help_text="computeResource",
        required=False,
        allow_null=True)


class AccessInfoSerializer(serializers.Serializer):
    tenant = serializers.CharField(
        help_text="tenant",
        required=True,
        max_length=255,
        allow_null=True)
    username = serializers.CharField(
        help_text="username",
        required=True,
        max_length=255,
        allow_null=True)
    password = serializers.CharField(
        help_text="password",
        required=True,
        max_length=255,
        allow_null=True)


class InterfaceInfoSerializer(serializers.Serializer):
    vimType = serializers.CharField(
        help_text="vimType",
        required=True,
        max_length=255,
        allow_null=True)
    apiVersion = serializers.CharField(
        help_text="apiVersion",
        required=True,
        max_length=255,
        allow_null=True)
    protocolType = serializers.ChoiceField(
        help_text="protocolType",
        choices=["http", "https"],
        required=True)


class VimInfoSerializer(serializers.Serializer):
    vimInfoId = serializers.CharField(
        help_text="vimInfoId",
        required=False,
        max_length=255,
        allow_null=True)
    vimId = serializers.CharField(
        help_text="vimId",
        required=False,
        max_length=255,
        allow_null=True)
    interfaceEndpoint = serializers.CharField(
        help_text="interfaceEndpoint",
        required=False,
        max_length=255,
        allow_null=True)
    interfaceInfo = InterfaceInfoSerializer(
        help_text="vimInfoId",
        required=False,
        allow_null=True)
    accessInfo = AccessInfoSerializer(
        help_text="accessInfo",
        required=False,
        allow_null=True)


class LinkPortsSerializer(serializers.Serializer):
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


class ResourceHandleSerializer(serializers.Serializer):
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
    resourceProviderId = serializers.CharField(
        help_text="resourceProviderId",
        required=False,
        max_length=255,
        allow_null=True)


class ExtVirtualLinkInfoSerializer(serializers.Serializer):
    extVirtualLinkId = serializers.CharField(
        help_text="extVirtualLinkId",
        required=True,
        max_length=255,
        allow_null=True)
    resourceHandle = ResourceHandleSerializer(
        help_text="iPAddress",
        required=True)
    linkPorts = LinkPortsSerializer(
        help_text="iPAddress",
        many=True,
        allow_null=True)


class L3AddressDataSerializer(serializers.Serializer):
    iPAddressType = serializers.ChoiceField(
        help_text="iPAddressType",
        choices=["IPv4", "IPv6"],
        required=True)
    iPAddress = serializers.CharField(
        help_text="iPAddress",
        required=True,
        max_length=255,
        allow_null=True)


class NetworkAddressSerializer(serializers.Serializer):
    addressType = serializers.ChoiceField(
        help_text="addressType",
        choices=["MAC", "IP"],
        required=True)
    l2AddressData = serializers.CharField(
        help_text="l2AddressData",
        required=False,
        max_length=255,
        allow_null=True)
    l3AddressData = L3AddressDataSerializer(
        help_text="addresses",
        required=False)


class ExtCpInfoSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(
        help_text="cpInstanceId",
        required=False,
        max_length=255,
        allow_null=True)
    cpdId = serializers.CharField(
        help_text="cpdId",
        required=True,
        max_length=255,
        allow_null=True)
    numDynamicAddresses = serializers.CharField(
        help_text="numDynamicAddresses",
        required=False,
        max_length=255,
        allow_null=True)
    addresses = NetworkAddressSerializer(
        help_text="addresses",
        many=True,
        allow_null=True)


class ScaleInfoSerializer(serializers.Serializer):
    aspectId = serializers.CharField(
        help_text="aspectId",
        required=True,
        max_length=255,
        allow_null=True)
    scaleLevel = serializers.IntegerField(
        help_text="scaleLevel",
        required=True)


class instantiatedVnfInfoSerializer(serializers.Serializer):
    flavourId = serializers.CharField(
        help_text="flavourId",
        required=True,
        max_length=255,
        allow_null=True)
    vnfState = serializers.ChoiceField(
        help_text="vnfState",
        choices=["STARTED", "STOPPED", "NOT_INSTANTIATED", "INSTANTIATED"],
        required=True,
        allow_null=True)
    scaleStatus = ScaleInfoSerializer(
        help_text="scaleStatus",
        many=True)
    extCpInfo = ExtCpInfoSerializer(
        help_text="extCpInfo",
        many=True)
    extVirtualLink = ExtVirtualLinkInfoSerializer(
        help_text="extVirtualLink",
        many=True)
    monitoringParameters = serializers.DictField(
        help_text="monitoringParameters",
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_null=True)
    vimInfo = VimInfoSerializer(
        help_text="vimInfo",
        many=True)
    vnfcResourceInfo = VnfcResourceInfoSerializer(
        help_text="vnfcResourceInfo",
        many=True)
    virtualLinkResourceInfo = VirtualLinkResourceInfoSerializer(
        help_text="virtualLinkResourceInfo",
        many=True)
    virtualStorageResourceInfo = VirtualStorageResourceInfoSerializer(
        help_text="virtualStorageResourceInfo",
        many=True)


class VnfInfoSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(
        help_text="vnfInstanceId",
        required=True,
        max_length=255,
        allow_null=True)
    vnfInstanceName = serializers.CharField(
        help_text="vnfInstanceName",
        required=True,
        max_length=255,
        allow_null=True)
    onboardedVnfPkgInfoId = serializers.CharField(
        help_text="onboardedVnfPkgInfoId",
        required=False,
        max_length=255,
        allow_null=True)
    vnfdVersion = serializers.CharField(
        help_text="vnfdVersion",
        required=False,
        max_length=255,
        allow_null=True,
        allow_blank=True)
    vnfProvider = serializers.CharField(
        help_text="vnfProvider",
        required=False,
        max_length=255,
        allow_null=True,
        allow_blank=True)
    instantiatedVnfInfo = instantiatedVnfInfoSerializer(
        help_text="instantiatedVnfInfo",
        required=True)


class VnfsInfoSerializer(serializers.ListSerializer):
    child = VnfInfoSerializer()


class ExtVirtualLinkSerizlizer(serializers.Serializer):
    vlInstanceId = serializers.CharField(
        help_text="vlInstanceId",
        required=False,
        max_length=255,
        allow_null=True)
    resourceSubnetId = serializers.CharField(
        help_text="resourceSubnetId",
        required=False,
        max_length=255,
        allow_null=True)
    cpdId = serializers.CharField(
        help_text="cpdId",
        required=False,
        max_length=255,
        allow_null=True)
    resourceId = serializers.CharField(
        help_text="resourceId",
        required=False,
        max_length=255,
        allow_null=True)
    vim = VimInfoSerializer(
        help_text="vim",
        required=False,
        allow_null=True)
    extCps = ExtCpInfoSerializer(
        help_text="extCps",
        many=True,
        required=False,
        allow_null=True)


class AdditionalParamsSerializer(serializers.Serializer):
    vimId = serializers.CharField(
        help_text="vimId",
        required=False,
        max_length=255,
        allow_null=True)
    inputs = serializers.DictField(
        help_text="inputs",
        child=serializers.CharField(help_text="custom key-value", allow_blank=True),
        required=False,
        allow_null=True)
    extVirtualLinks = serializers.ListSerializer(
        help_text="extVirtualLinks",
        child=ExtVirtualLinkSerizlizer(help_text="extVirtualLinks", required=False, allow_null=True),
        required=False,
        allow_null=True)


class InstantiateVnfRequestSerializer(serializers.Serializer):
    flavourId = serializers.CharField(
        help_text="flavourId",
        required=True,
        max_length=255,
        allow_null=True)
    instantiationLevelId = serializers.CharField(
        help_text="instantiationLevelId",
        required=True,
        max_length=255,
        allow_null=True)
    localizationLanguage = serializers.CharField(
        help_text="localizationLanguage",
        required=True,
        max_length=255,
        allow_null=True)
    vnfmId = serializers.CharField(
        help_text="vnfmId",
        required=False,
        max_length=255,
        allow_null=True)
    extVirtualLinks = serializers.ListSerializer(
        help_text="extVirtualLinks",
        child=ExtVirtualLinkSerizlizer(help_text="extVirtualLinks", required=False, allow_null=True),
        required=False,
        allow_null=True)
    additionalParams = AdditionalParamsSerializer(
        help_text="additionalParams",
        required=False,
        allow_null=True)


class InstOrTeriVnfResponseSerializer(serializers.Serializer):
    jobId = serializers.CharField(
        help_text="jobId",
        required=True,
        max_length=255,
        allow_null=True)


class TerminateVnfRequestSerializer(serializers.Serializer):
    terminationType = serializers.CharField(
        help_text="terminationType",
        required=True,
        max_length=255,
        allow_null=True)
    gracefulTerminationTimeout = serializers.IntegerField(
        help_text="gracefulTerminationTimeout",
        default=120,
        required=False)
