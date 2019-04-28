# Copyright 2019 ZTE Corporation.
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

from django.contrib import admin

from lcm.pub.database.models import NfInstModel
from lcm.pub.database.models import NfvoRegInfoModel
from lcm.pub.database.models import StorageInstModel
from lcm.pub.database.models import VmInstModel
from lcm.pub.database.models import VNFCInstModel
from lcm.pub.database.models import FlavourInstModel
from lcm.pub.database.models import NetworkInstModel
from lcm.pub.database.models import SubNetworkInstModel
from lcm.pub.database.models import VLInstModel
from lcm.pub.database.models import PortInstModel
from lcm.pub.database.models import CPInstModel
from lcm.pub.database.models import SubscriptionModel
from lcm.pub.database.models import VNFLcmOpOccModel


@admin.register(NfInstModel)
class NfInstModelAdmin(admin.ModelAdmin):
    list_display_links = ('nfinstid', 'nf_name')
    fields = [
        "nfinstid",
        "nf_name",
        "vnfminstid",
        "package_id",
        "status",
        "flavour_id",
        "location",
        "version",
        "vendor",
        "netype",
        "vnfd_model",
        "input_params",
        "create_time",
        "lastuptime",
        "nf_desc",
        "vnfdid",
        "vnfSoftwareVersion",
        "vnfConfigurableProperties",
        "localizationLanguage",
        "operationState",
        "resInfo",
        "vimInfo"
    ]

    list_display = [
        "nfinstid",
        "nf_name",
        "vnfminstid",
        "package_id",
        "status",
        "flavour_id",
        "location",
        "version",
        "vendor",
        "netype",
        "vnfd_model",
        "input_params",
        "create_time",
        "lastuptime",
        "nf_desc",
        "vnfdid",
        "vnfSoftwareVersion",
        "vnfConfigurableProperties",
        "localizationLanguage",
        "operationState",
        "resInfo",
        "vimInfo"
    ]

    search_fields = (
        "nfinstid",
        "nf_name",
        "vnfminstid",
        "package_id"
    )


@admin.register(NfvoRegInfoModel)
class NfvoRegInfoModelAdmin(admin.ModelAdmin):
    list_display_links = ('nfvoid', 'vnfminstid')
    fields = [
        "nfvoid",
        "vnfminstid",
        "apiurl",
        "nfvouser",
        "nfvopassword",
        "authtype",
        "clientcert",
        "servercert",
        "regtime"
    ]

    list_display = (
        "nfvoid",
        "vnfminstid",
        "apiurl",
        "nfvouser",
        "nfvopassword",
        "authtype",
        "clientcert",
        "servercert",
        "regtime"
    )

    search_fields = (
        "nfvoid",
        "vnfminstid"
    )


@admin.register(StorageInstModel)
class StorageInstModelAdmin(admin.ModelAdmin):
    list_display_links = ('storageid', 'vimid')
    fields = [
        "storageid",
        "vimid",
        "resourceid",
        "insttype",
        "instid",
        "name",
        "storagetype",
        "size",
        "tenant",
        "is_predefined",
        "create_time",
        "nodeId"
    ]

    list_display = (
        "storageid",
        "vimid",
        "resourceid",
        "insttype",
        "instid",
        "name",
        "storagetype",
        "size",
        "tenant",
        "is_predefined",
        "create_time",
        "nodeId"
    )

    search_fields = (
        "storageid",
        "vimid",
        "resourceid",
        "instid"
    )


@admin.register(VmInstModel)
class VmInstModelAdmin(admin.ModelAdmin):
    list_display_links = ('vmid', 'vimid')
    fields = [
        "vmid",
        "vimid",
        "tenant",
        "resourceid",
        "vmname",
        "nic_array",
        "metadata",
        "volume_array",
        "server_group",
        "availability_zone",
        "flavor_id",
        "security_groups",
        "operationalstate",
        "insttype",
        "is_predefined",
        "create_time",
        "instid",
        "nodeId"
    ]

    list_display = [
        "vmid",
        "vimid",
        "tenant",
        "resourceid",
        "vmname",
        "nic_array",
        "metadata",
        "volume_array",
        "server_group",
        "availability_zone",
        "flavor_id",
        "security_groups",
        "operationalstate",
        "insttype",
        "is_predefined",
        "create_time",
        "instid",
        "nodeId"
    ]

    search_fields = (
        "vmid",
        "vimid",
        "tenant",
        "resourceid",
        "vmname"
    )


@admin.register(VNFLcmOpOccModel)
class VNFLcmOpOccModelAdmin(admin.ModelAdmin):
    list_display_links = ('id', 'operation_state')
    fields = [
        "id",
        "operation_state",
        "state_entered_time",
        "start_time",
        "vnf_instance_id",
        "operation",
        "error",
        "sub_operation",
        "operation_params",
        "links"
    ]

    list_display = [
        "id",
        "operation_state",
        "state_entered_time",
        "start_time",
        "vnf_instance_id",
        "operation",
        "error",
        "sub_operation",
        "operation_params",
        "links"
    ]

    search_fields = (
        "id",
        "vnf_instance_id"
    )


admin.site.register(VNFCInstModel)
admin.site.register(FlavourInstModel)
admin.site.register(NetworkInstModel)
admin.site.register(SubNetworkInstModel)
admin.site.register(VLInstModel)
admin.site.register(PortInstModel)
admin.site.register(CPInstModel)
admin.site.register(SubscriptionModel)
admin.site.register(VNFLcmOpOccModel)
