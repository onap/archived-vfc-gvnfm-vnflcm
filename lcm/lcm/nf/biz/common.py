# Copyright 2017 ZTE Corporation.
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

import uuid

from lcm.pub.database.models import VmInstModel, NetworkInstModel, \
    SubNetworkInstModel, PortInstModel, StorageInstModel, FlavourInstModel, VNFCInstModel
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.values import ignore_case_get, get_none, get_boolean, get_integer


def volume_save(job_id, nf_inst_id, ret):
    JobUtil.add_job_status(job_id, 25, 'Create vloumns!')
    StorageInstModel.objects.create(
        storageid=str(uuid.uuid4()),
        vimid=ignore_case_get(ret, "vimId"),
        resourceid=ignore_case_get(ret, "id"),
        name=ignore_case_get(ret, "name"),
        tenant=ignore_case_get(ret, "tenantId"),
        create_time=ignore_case_get(ret, "createTime"),
        storagetype=get_none(ignore_case_get(ret, "type")),
        size=ignore_case_get(ret, "size"),
        insttype=0,
        is_predefined=ignore_case_get(ret, "returnCode"),
        nodeId=ignore_case_get(ret, "nodeId"),
        instid=nf_inst_id)


def network_save(job_id, nf_inst_id, ret):
    JobUtil.add_job_status(job_id, 35, 'Create networks!')
    NetworkInstModel.objects.create(
        networkid=str(uuid.uuid4()),
        name=ignore_case_get(ret, "name"),
        vimid=ignore_case_get(ret, "vimId"),
        resourceid=ignore_case_get(ret, "id"),
        tenant=ignore_case_get(ret, "tenantId"),
        segmentid=str(ignore_case_get(ret, "segmentationId")),
        network_type=ignore_case_get(ret, "networkType"),
        physicalNetwork=ignore_case_get(ret, "physicalNetwork"),
        vlantrans=get_boolean(ignore_case_get(ret, "vlanTransparent")),
        is_shared=get_boolean(ignore_case_get(ret, "shared")),
        routerExternal=get_boolean(ignore_case_get(ret, "routerExternal")),
        insttype=0,
        is_predefined=ignore_case_get(ret, "returnCode"),
        nodeId=ignore_case_get(ret, "nodeId"),
        instid=nf_inst_id)


def subnet_save(job_id, nf_inst_id, ret):
    JobUtil.add_job_status(job_id, 40, 'Create subnets!')
    SubNetworkInstModel.objects.create(
        subnetworkid=str(uuid.uuid4()),
        name=ignore_case_get(ret, "name"),
        vimid=ignore_case_get(ret, "vimId"),
        resourceid=ignore_case_get(ret, "id"),
        tenant=ignore_case_get(ret, "tenantId"),
        networkid=ignore_case_get(ret, "networkId"),
        cidr=ignore_case_get(ret, "cidr"),
        ipversion=ignore_case_get(ret, "ipversion"),
        isdhcpenabled=ignore_case_get(ret, "enableDhcp"),
        gatewayip=ignore_case_get(ret, "gatewayIp"),
        dnsNameservers=ignore_case_get(ret, "dnsNameservers"),
        hostRoutes=ignore_case_get(ret, "hostRoutes"),
        allocationPools=ignore_case_get(ret, "allocationPools"),
        insttype=0,
        is_predefined=ignore_case_get(ret, "returnCode"),
        instid=nf_inst_id)


def port_save(job_id, nf_inst_id, ret):
    JobUtil.add_job_status(job_id, 50, 'Create ports!')
    PortInstModel.objects.create(
        portid=str(uuid.uuid4()),
        networkid=ignore_case_get(ret, "networkId"),
        subnetworkid=ignore_case_get(ret, "subnetId"),
        name=ignore_case_get(ret, "name"),
        vimid=ignore_case_get(ret, "vimId"),
        resourceid=ignore_case_get(ret, "id"),
        tenant=ignore_case_get(ret, "tenantId"),
        macaddress=ignore_case_get(ret, "macAddress"),
        ipaddress=ignore_case_get(ret, "ip"),
        typevirtualnic=ignore_case_get(ret, "vnicType"),
        securityGroups=ignore_case_get(ret, "securityGroups"),
        insttype=0,
        is_predefined=ignore_case_get(ret, "returnCode"),
        nodeId=ignore_case_get(ret, "nodeId"),
        instid=nf_inst_id)


def flavor_save(job_id, nf_inst_id, ret):
    JobUtil.add_job_status(job_id, 60, 'Create flavors!')
    FlavourInstModel.objects.create(
        flavourid=str(uuid.uuid4()),
        name=ignore_case_get(ret, "name"),
        vimid=ignore_case_get(ret, "vimId"),
        resourceid=ignore_case_get(ret, "id"),
        tenant=ignore_case_get(ret, "tenantId"),
        vcpu=get_integer(ignore_case_get(ret, "vcpu")),
        memory=get_integer(ignore_case_get(ret, "memory")),
        disk=get_integer(ignore_case_get(ret, "disk")),
        ephemeral=get_integer(ignore_case_get(ret, "ephemeral")),
        swap=get_integer(ignore_case_get(ret, "swap")),
        isPublic=get_boolean(ignore_case_get(ret, "isPublic")),
        extraspecs=ignore_case_get(ret, "extraSpecs"),
        is_predefined=ret.get("returnCode", int(0)),
        instid=nf_inst_id)


def vm_save(job_id, nf_inst_id, ret):
    JobUtil.add_job_status(job_id, 70, 'Create vms!')
    vm_id = str(uuid.uuid4())
    nics = ignore_case_get(ret, "nicArray")
    VmInstModel.objects.create(
        vmid=vm_id,
        vmname=ignore_case_get(ret, "name"),
        vimid=ignore_case_get(ret, "vimId"),
        resourceid=ignore_case_get(ret, "id"),
        tenant=ignore_case_get(ret, "tenantId"),
        nic_array=nics if nics else "null",
        metadata=ignore_case_get(ret, "metadata"),
        volume_array=ignore_case_get(ret, "volumeArray"),
        server_group=ignore_case_get(ret, "serverGroup"),
        availability_zone=str(ignore_case_get(ret, "availabilityZone", "undefined")),
        flavor_id=ignore_case_get(ret, "flavorId"),
        security_groups=ignore_case_get(ret, "securityGroups"),
        operationalstate=ignore_case_get(ret, "status"),
        insttype=0,
        is_predefined=ignore_case_get(ret, "returnCode"),
        instid=nf_inst_id)
    VNFCInstModel.objects.create(
        vnfcinstanceid=str(uuid.uuid4()),
        vduid=ignore_case_get(ret, "id"),
        is_predefined=ignore_case_get(ret, "returnCode"),
        instid=nf_inst_id,
        vmid=vm_id)
