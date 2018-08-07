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

from scale_info import ScaleInfoSerializer
from ext_cp_info import ExtCpInfoSerializer
from ext_virtual_link_info import ExtVirtualLinkInfoSerializer
from ext_managed_virtual_link_info import ExtManagedVirtualLinkInfoSerializer
from vnfc_resource_info import VnfcResourceInfoSerializer
from vnf_virtual_link_resource_info import VnfVirtualLinkResourceInfoSerializer
from virtual_storage_resource_info import VirtualStorageResourceInfoSerializer


class InstantiatedVnfInfoSerializer(serializers.Serializer):
    flavourId = serializers.CharField(
        help_text="Identifier of the VNF deployment flavour applied to this VNF instance.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    vnfState = serializers.ChoiceField(
        help_text="State of the VNF instance.",
        choices=["STARTED", "STOPPED", "NOT_INSTANTIATED", "INSTANTIATED", "FAILED"],
        required=True,
        allow_null=False,
        allow_blank=False)
    scaleStatus = ScaleInfoSerializer(
        help_text="Scale status of the VNF, one entry per aspect. \
        Represents for every scaling aspect how big the VNF has been scaled w.r.t. that aspect.",
        many=True,
        required=False,
        allow_null=True)
    extCpInfo = ExtCpInfoSerializer(
        help_text="Information about the external CPs exposed by the VNF instance.",
        many=True,
        required=True,
        allow_null=False)
    extVirtualLinkInfo = ExtVirtualLinkInfoSerializer(
        help_text="Information about the external VLs the VNF instance is connected to.",
        many=True,
        required=False,
        allow_null=True)
    extManagedVirtualLinkInfo = ExtManagedVirtualLinkInfoSerializer(
        help_text="Information about the externally-managed internal VLs of the VNF instance.",
        many=True,
        required=False,
        allow_null=True)
    monitoringParameters = serializers.DictField(
        help_text="Active monitoring parameters.",
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_null=True)
    localizationLanguage = serializers.CharField(
        help_text="Information about localization language of the VNF.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfcResourceInfo = VnfcResourceInfoSerializer(
        help_text="Information about the virtualised compute and storage resources used by the VNFCs of the VNF instance.",
        many=True,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfVirtualLinkResourceInfo = VnfVirtualLinkResourceInfoSerializer(
        help_text="Information about the virtualised network resources used by the VLs of the VNF instance.",
        many=True,
        required=False,
        allow_null=True,
        allow_blank=True)
    virtualStorageResourceInfo = VirtualStorageResourceInfoSerializer(
        help_text="Information about the virtualised storage resources used as storage for the VNF instance.",
        many=True,
        required=False,
        allow_null=True,
        allow_blank=True)