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

import logging
import sys
import time
import traceback

from lcm.pub.utils.values import ignore_case_get, set_opt_val
from . import api
from .exceptions import VimException

logger = logging.getLogger(__name__)

RES_EXIST, RES_NEW = 0, 1
NET_PRIVATE, NET_SHSRED = 0, 1
VLAN_TRANSPARENT_NO, VLAN_TRANSPARENT_YES = 0, 1
IP_V4, IP_V6 = 4, 6
DHCP_DISABLED, DHCP_ENABLED = 0, 1
OPT_CREATE_VOLUME = 20
OPT_CREATE_NETWORK = 30
OPT_CREATE_SUBNET = 40
OPT_CREATE_PORT = 50
OPT_CREATE_FLAVOR = 60
OPT_CREATE_VM = 80

BOOT_FROM_VOLUME = 1


def create_vim_res(data, do_notify, do_rollback):
    try:
        for vol in ignore_case_get(data, "volume_storages"):
            create_volume(vol, do_notify, OPT_CREATE_VOLUME)
        for network in ignore_case_get(data, "vls"):
            create_network(network, do_notify, OPT_CREATE_NETWORK)
        for subnet in ignore_case_get(data, "vls"):
            create_subnet(subnet, do_notify, OPT_CREATE_SUBNET)
        for port in ignore_case_get(data, "cps"):
            create_port(port, do_notify, OPT_CREATE_PORT)
        for flavor in ignore_case_get(data, "vdus"):
            create_flavor(flavor, do_notify, OPT_CREATE_FLAVOR)
        for vm in ignore_case_get(data, "vdus"):
            create_vm(vm, do_notify, OPT_CREATE_VM)
    except VimException as e:
        logger.error(e.message)
        do_rollback(e.message)
    except:
        logger.error(traceback.format_exc())
        do_rollback(str(sys.exc_info()))

def delete_vim_res(data, do_notify):
    res_types = ["vm", "flavor", "port", "subnet", "network", "volume"]
    res_del_funs = [api.delete_vm, api.delete_flavor, api.delete_port, 
        api.delete_subnet, api.delete_network, api.delete_volume]
    for res_type, res_del_fun in zip(res_types, res_del_funs):
        for res in ignore_case_get(data, res_type):
            try:
                res_del_fun(res["vim_id"], res["res_id"])
            except VimException as e:
                logger.error("Failed to delete %s(%s): %s", 
                    res_type, res["res_id"], e.message)
            do_notify(res_type)

def create_volume(vol, do_notify, progress):
    param = {
        "tenant": vol["properties"]["location_info"]["tenant"],	
        "volumeName": vol["properties"]["volume_name"],	
        "volumeSize": int(ignore_case_get(vol["properties"], "size", "0"))
    }
    set_opt_val(param, "imageName", ignore_case_get(vol, "image_file"))
    set_opt_val(param, "volumeType", ignore_case_get(vol["properties"], "custom_volume_type"))
    vim_id = vol["properties"]["location_info"]["vimid"],
    ret = api.create_volume(vim_id, param)
    vol_id, vol_name, return_code = ret["id"], ret["name"], ret["returnCode"]
    retry_count, max_retry_count = 0, 300
    while retry_count < max_retry_count:
        vol_info = api.get_volume(vim_id, vol_id)
        if vol_info["status"].upper() == "AVAILABLE":
            do_notify(progress, ret)
            break
        time.sleep(2)
        retry_count = retry_count + 1
    if return_code == RES_NEW:
        api.delete_volume(vim_id, vol_id)
    raise VimException("Failed to create Volume(%s): Timeout." % vol_name, "500")
    
def create_network(network, do_notify, progress):
    param = {
        "tenant": network["properties"]["location_info"]["tenant"],	
        "networkName": network["properties"]["network_name"],
        "shared": NET_PRIVATE,
        "networkType": network["properties"]["network_type"],
        "physicalNetwork": ignore_case_get(network["properties"], "physical_network")
    }
    set_opt_val(param, "vlanTransparent", 
        ignore_case_get(network["properties"], "vlan_transparent"), VLAN_TRANSPARENT_YES)
    set_opt_val(param, "segmentationId", ignore_case_get(network["properties"], "segmentation_id"))
    vim_id = network["properties"]["location_info"]["vimid"],
    ret = api.create_network(vim_id, param)
    do_notify(progress, ret)
    
def create_subnet(subnet, do_notify, progress):
    param = {
        "tenant": subnet["properties"]["location_info"]["tenant"],	
        "networkName": subnet["properties"]["network_name"],
        "subnetName": subnet["properties"]["name"],
        "cidr": ignore_case_get(subnet["properties"], "cidr"),
        "ipVersion": ignore_case_get(subnet["properties"], "ip_version", IP_V4)
    }
    set_opt_val(param, "enableDhcp", 
        ignore_case_get(subnet["properties"], "dhcp_enabled"), DHCP_ENABLED)
    set_opt_val(param, "gatewayIp", ignore_case_get(subnet["properties"], "gateway_ip"))
    set_opt_val(param, "dnsNameservers", ignore_case_get(subnet["properties"], "dns_nameservers"))
    allocation_pool = {}
    set_opt_val(allocation_pool, "start", ignore_case_get(subnet["properties"], "start_ip"))
    set_opt_val(allocation_pool, "end", ignore_case_get(subnet["properties"], "end_ip"))
    if allocation_pool:
        param["allocationPools"] = [allocation_pool]
    set_opt_val(param, "hostRoutes", ignore_case_get(subnet["properties"], "host_routes"))
    vim_id = subnet["properties"]["location_info"]["vimid"],
    ret = api.create_subnet(vim_id, param)
    do_notify(progress, ret)
    
def create_port(port, do_notify, progress):
    param = {
        "tenant": port["properties"]["location_info"]["tenant"],
        "networkName": port["properties"]["network_name"],
        "subnetName": port["properties"]["name"],
        "portName": port["properties"]["name"]
    }
    vim_id = port["properties"]["location_info"]["vimid"],
    ret = api.create_subnet(vim_id, param)
    do_notify(progress, ret)

def create_flavor(flavor, do_notify, progress):
    param = {
        "tenant": flavor["properties"]["location_info"]["tenant"],
        "vcpu": int(flavor["nfv_compute"]["num_cpus"]),
        "memory": int(flavor["nfv_compute"]["mem_size"].replace('MB', '').strip())
    }
    set_opt_val(param, "extraSpecs", ignore_case_get(flavor["nfv_compute"], "flavor_extra_specs"))
    vim_id = flavor["properties"]["location_info"]["vimid"],
    ret = api.create_flavor(vim_id, param)
    do_notify(progress, ret)
    
def create_vm(vm, do_notify, progress):
    param = {
        "tenant": vm["properties"]["location_info"]["tenant"],
        "vmName": vm["properties"]["name"],
        "boot": {
            "type": BOOT_FROM_VOLUME,
            "volumeName": vm["volume_storages"][0]["volume_storage_id"]
        },
        "nicArray": [],
        "contextArray": [],
        "volumeArray": []
    }
    set_opt_val(param, "availabilityZone", 
        ignore_case_get(vm["properties"]["location_info"], "availability_zone"))
    for inject_data in ignore_case_get(vm["properties"], "inject_data_list"):
        param["contextArray"].append({
            "fileName": inject_data["file_name"],
            "fileData": inject_data["file_data"]
        })
    for vol_data in vm["volume_storages"]:
        param["contextArray"].append(vol_data["volume_storage_id"])
    # nicArray TODO:
    vim_id = vm["properties"]["location_info"]["vimid"],
    ret = api.create_vm(vim_id, param)
    vm_id, vm_name, return_code = ret["id"], ret["name"], ret["returnCode"]
    opt_vm_status = "Timeout"
    retry_count, max_retry_count = 0, 100
    while retry_count < max_retry_count:
        vm_info = api.get_vm(vim_id, vm_id)
        if vm_info["status"].upper() == "ACTIVE":
            do_notify(progress, ret)
            break
        if vm_info["status"].upper() == "ERROR":
            opt_vm_status = vm_info["status"]
            break
        time.sleep(2)
        retry_count = retry_count + 1
    if return_code == RES_NEW:
        api.delete_vm(vim_id, vm_id)
    raise VimException("Failed to create Vm(%s): %s." % (vm_name, opt_vm_status), "500")
