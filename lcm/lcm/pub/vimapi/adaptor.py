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
import time
import json
import os
import base64

from lcm.pub.utils.values import ignore_case_get, set_opt_val
from . import api
from .exceptions import VimException
from lcm.pub.exceptions import NFLCMException
from lcm.nf.const import ACTION_TYPE, HEAL_ACTION_TYPE

logger = logging.getLogger(__name__)

ERR_CODE = "500"
RES_EXIST, RES_NEW = 0, 1
IP_V4, IP_V6 = 4, 6
BOOT_FROM_VOLUME, BOOT_FROM_IMAGE = 1, 2

RES_VOLUME = "volume"
RES_NETWORK = "network"
RES_SUBNET = "subnet"
RES_PORT = "port"
RES_FLAVOR = "flavor"
RES_VM = "vm"
NOT_PREDEFINED = 1


def get_tenant_id(vim_cache, vim_id, tenant_name):
    if vim_id not in vim_cache:
        tenants = api.list_tenant(vim_id)
        vim_cache[vim_id] = {}
        for tenant in tenants["tenants"]:
            id, name = tenant["id"], tenant["name"]
            vim_cache[vim_id][name] = id
    if tenant_name not in vim_cache[vim_id]:
        raise VimException("Tenant(%s) not found in vim(%s)" % (tenant_name, vim_id), ERR_CODE)
    return vim_cache[vim_id][tenant_name]


def set_res_cache(res_cache, res_type, key, val):
    if res_type not in res_cache:
        res_cache[res_type] = {}
    if key in res_cache[res_type]:
        raise VimException("Duplicate key(%s) of %s" % (key, res_type), ERR_CODE)
    res_cache[res_type][key] = val


def get_res_id(res_cache, res_type, key):
    if res_type not in res_cache:
        raise VimException("%s not found in cache" % res_type, ERR_CODE)
    if key not in res_cache[res_type]:
        raise VimException("%s(%s) not found in cache" % (res_type, key), ERR_CODE)
    return res_cache[res_type][key]


def action_vm(action_type, server, vimId, tenantId):
    param = {}
    if action_type == ACTION_TYPE.START:
        param = {
            "os-start": None,
        }
    elif action_type == ACTION_TYPE.STOP:
        param = {
            "os-stop": None,
        }
    elif action_type == ACTION_TYPE.REBOOT:
        param = {
            "reboot": {}
        }
        if server["status"] == "ACTIVE":
            param["reboot"]["type"] = "SOFT"
        else:
            param["reboot"]["type"] = "HARD"
    res_id = server["id"]
    logger.debug("%s,%s,%s,%s", vimId, tenantId, res_id, param)
    api.action_vm(vimId, tenantId, res_id, param)


# TODO Have to check if the resources should be started and stopped in some order.
def operate_vim_res(data, changeStateTo, stopType, gracefulStopTimeout, do_notify_op):
    for res in ignore_case_get(data, "vm"):
        try:
            if changeStateTo == "STARTED":
                action_vm(ACTION_TYPE.START, res, res["vim_id"], res["tenant_id"])
                do_notify_op("ACTIVE", res["id"])
            elif changeStateTo == "STOPPED":
                if stopType == "GRACEFUL":
                    if gracefulStopTimeout > 60:
                        gracefulStopTimeout = 60
                    time.sleep(gracefulStopTimeout)
                action_vm(ACTION_TYPE.STOP, res, res["vim_id"], res["tenant_id"])
                do_notify_op("INACTIVE", res["id"])
        except VimException as e:
            logger.error("Failed to Operate %s(%s)", RES_VM, res["res_id"])
            logger.error("%s:%s", e.http_code, e.args[0])
            raise NFLCMException("Failed to Operate %s(%s)", RES_VM, res["res_id"])


def heal_vim_res(vdus, vnfd_info, do_notify, data, vim_cache, res_cache):
    try:
        vimid = data["vimid"]
        tenant = data["tenant"]
        actionType = data["action"]
        resid = ''
        if actionType == HEAL_ACTION_TYPE.START:
            resid = vdus[0]["vdu_id"]
            create_vm(vim_cache, res_cache, vnfd_info, vdus[0], do_notify, RES_VM)
        elif actionType == HEAL_ACTION_TYPE.RESTART:
            resid = vdus[0].resourceid
            logger.debug("Start restart vm(%s)", resid)
            vm_info = api.get_vm(vimid, tenant, vdus[0].resourceid)
            logger.debug("vminfo=%s", vm_info)
            action_vm(ACTION_TYPE.REBOOT, vm_info, vimid, tenant)
    except VimException as e:
        logger.error("Failed to Heal %s(%s)", RES_VM, resid)
        logger.error("%s:%s", e.http_code, e.args[0])
        raise NFLCMException("Failed to Heal %s(%s)" % (RES_VM, resid))


def create_vim_res(data, do_notify, vim_cache={}, res_cache={}):
    for vol in ignore_case_get(data, "volume_storages"):
        create_volume(vim_cache, res_cache, vol, do_notify, RES_VOLUME)
    for network in ignore_case_get(data, "vls"):
        create_network(vim_cache, res_cache, network, do_notify, RES_NETWORK)
    for subnet in ignore_case_get(data, "vls"):
        create_subnet(vim_cache, res_cache, subnet, do_notify, RES_SUBNET)
    for port in ignore_case_get(data, "cps"):
        create_port(vim_cache, res_cache, data, port, do_notify, RES_PORT)
    for vdu in ignore_case_get(data, "vdus"):
        if vdu["type"] == "tosca.nodes.nfv.Vdu.Compute":
            create_flavor(vim_cache, res_cache, data, vdu, do_notify, RES_FLAVOR)
    for vdu in ignore_case_get(data, "vdus"):
        if vdu["type"] == "tosca.nodes.nfv.Vdu.Compute":
            create_vm(vim_cache, res_cache, data, vdu, do_notify, RES_VM)


def delete_vim_res(data, do_notify):
    res_types = [RES_VM, RES_FLAVOR, RES_PORT, RES_SUBNET, RES_NETWORK, RES_VOLUME]
    res_del_funs = [api.delete_vm, api.delete_flavor, api.delete_port,
                    api.delete_subnet, api.delete_network, api.delete_volume]
    for res_type, res_del_fun in zip(res_types, res_del_funs):
        for res in ignore_case_get(data, res_type):
            try:
                if NOT_PREDEFINED == res["is_predefined"]:
                    res_del_fun(res["vim_id"], res["tenant_id"], res["res_id"])
            except VimException as e:
                logger.error("Failed to delete %s(%s)", res_type, res["res_id"])
                logger.error("%s:%s", e.http_code, e.args[0])
            do_notify(res_type, res["res_id"])


def create_volume(vim_cache, res_cache, vol, do_notify, res_type):
    location_info = vol["properties"]["location_info"]
    param = {
        "name": vol["properties"]["volume_name"] if vol["properties"].get("volume_name", None) else vol["volume_storage_id"],
        "volumeSize": int(ignore_case_get(vol["properties"], "size_of_storage", "0").replace('GB', '').replace('"', '').strip())
    }
    set_opt_val(param, "imageName", ignore_case_get(vol, "image_file"))
    set_opt_val(param, "volumeType", ignore_case_get(vol["properties"], "type_of_storage"))
    set_opt_val(param, "availabilityZone", ignore_case_get(location_info, "availability_zone"))
    vim_id, tenant_name = location_info["vimid"], location_info["tenant"]
    tenant_id = get_tenant_id(vim_cache, vim_id, tenant_name)
    ret = api.create_volume(vim_id, tenant_id, param)
    ret["nodeId"] = vol["volume_storage_id"]
    do_notify(res_type, ret)
    vol_id, vol_name = ret["id"], ret["name"]
    set_res_cache(res_cache, res_type, vol["volume_storage_id"], vol_id)
    retry_count, max_retry_count = 0, 300
    while retry_count < max_retry_count:
        vol_info = api.get_volume(vim_id, tenant_id, vol_id)
        if vol_info["status"].upper() == "AVAILABLE":
            logger.debug("Volume(%s) is available", vol_id)
            return
        time.sleep(2)
        retry_count = retry_count + 1
    raise VimException("Failed to create Volume(%s): Timeout." % vol_name, ERR_CODE)


def create_network(vim_cache, res_cache, network, do_notify, res_type):
    location_info = network["properties"]["location_info"]
    vl_profile = network["properties"]["vl_profile"]
    param = {
        "name": vl_profile["networkName"],
        "shared": False,
        "networkType": ignore_case_get(vl_profile, "networkType"),
        "physicalNetwork": ignore_case_get(vl_profile, "physicalNetwork")
    }
    set_opt_val(param, "vlanTransparent", ignore_case_get(vl_profile, "vlanTransparent"))
    set_opt_val(param, "segmentationId", int(ignore_case_get(vl_profile, "segmentationId", "0")))
    set_opt_val(param, "routerExternal", ignore_case_get(network, "route_external"))
    vim_id, tenant_name = location_info["vimid"], location_info["tenant"]
    tenant_id = get_tenant_id(vim_cache, vim_id, tenant_name)
    ret = api.create_network(vim_id, tenant_id, param)
    ret["nodeId"] = network["vl_id"]
    do_notify(res_type, ret)
    set_res_cache(res_cache, res_type, network["vl_id"], ret["id"])


def create_subnet(vim_cache, res_cache, subnet, do_notify, res_type):
    location_info = subnet["properties"]["location_info"]
    network_id = get_res_id(res_cache, RES_NETWORK, subnet["vl_id"])
    vl_profile = subnet["properties"]["vl_profile"]
    layer_protocol = ignore_case_get(subnet["properties"]["connectivity_type"], "layer_protocol")
    param = {
        "networkId": network_id,
        "name": vl_profile["networkName"] + "_subnet",
        "cidr": ignore_case_get(vl_profile, "cidr"),
        "ipVersion": IP_V4 if(layer_protocol == 'ipv4') else (IP_V6 if(layer_protocol == 'ipv6') else None)
    }
    set_opt_val(param, "enableDhcp", ignore_case_get(vl_profile, "dhcpEnabled"))
    set_opt_val(param, "gatewayIp", ignore_case_get(vl_profile, "gatewayIp"))
    set_opt_val(param, "dnsNameservers", ignore_case_get(subnet["properties"], "dns_nameservers"))
    allocation_pool = {}
    set_opt_val(allocation_pool, "start", ignore_case_get(vl_profile, "startIp"))
    set_opt_val(allocation_pool, "end", ignore_case_get(vl_profile, "endIp"))
    if allocation_pool:
        param["allocationPools"] = [allocation_pool]
    set_opt_val(param, "hostRoutes", ignore_case_get(subnet["properties"], "host_routes"))
    vim_id, tenant_name = location_info["vimid"], location_info["tenant"]
    tenant_id = get_tenant_id(vim_cache, vim_id, tenant_name)
    ret = api.create_subnet(vim_id, tenant_id, param)
    do_notify(res_type, ret)
    set_res_cache(res_cache, res_type, subnet["vl_id"], ret["id"])


def create_port(vim_cache, res_cache, data, port, do_notify, res_type):
    location_info = None
    port_ref_vdu_id = ignore_case_get(port, "vdu_id")
    for vdu in ignore_case_get(data, "vdus"):
        if vdu["vdu_id"] == port_ref_vdu_id:
            location_info = vdu["properties"]["location_info"]
            if port["cp_id"] not in vdu["cps"]:
                vdu["cps"].append(port["cp_id"])
            break
    if not location_info:
        err_msg = "vdu_id(%s) for cp(%s) is not defined."
        raise VimException(err_msg % (port_ref_vdu_id, port["cp_id"]), ERR_CODE)
    network_id = ignore_case_get(port, "networkId")
    subnet_id = ignore_case_get(port, "subnetId")

    if not network_id:
        if port["vl_id"] == "":
            return
        network_id = get_res_id(res_cache, RES_NETWORK, port["vl_id"])
        subnet_id = get_res_id(res_cache, RES_SUBNET, port["vl_id"])
    param = {
        "networkId": network_id,
        "name": port["cp_id"]
    }
    set_opt_val(param, "subnetId", subnet_id)
    set_opt_val(param, "macAddress", ignore_case_get(port["properties"], "mac_address"))
    ip_address = []
    logger.debug("port['properties']:%s" % port["properties"])
    for one_protocol_data in port["properties"]["protocol_data"]:
        l3_address_data = one_protocol_data["address_data"]["l3_address_data"]  # l3 is not 13
        fixed_ip_address = ignore_case_get(l3_address_data, "fixed_ip_address")
        ip_address.extend(fixed_ip_address)
    for one_virtual_network_interface in port["properties"].get("virtual_network_interface_requirements", []):
        network_interface_requirements = one_virtual_network_interface["network_interface_requirements"]
        interfaceTypeString = ignore_case_get(network_interface_requirements, "interfaceType")
        interfaceType = ""
        if interfaceTypeString != "":
            interfaceType = json.loads(interfaceTypeString)["configurationValue"]
        vnic_type = ignore_case_get(port["properties"], "vnic_type")
        if vnic_type == "":
            if interfaceType == "SR-IOV":
                set_opt_val(param, "vnicType", "direct")
        else:
            set_opt_val(param, "vnicType", vnic_type)

    set_opt_val(param, "ip", ",".join(ip_address))
    set_opt_val(param, "securityGroups", "")   # TODO
    vim_id, tenant_name = location_info["vimid"], location_info["tenant"]
    tenant_id = get_tenant_id(vim_cache, vim_id, tenant_name)
    ret = api.create_port(vim_id, tenant_id, param)
    ret["nodeId"] = port["cp_id"]
    do_notify(res_type, ret)
    set_res_cache(res_cache, res_type, port["cp_id"], ret["id"])


def create_flavor(vim_cache, res_cache, data, flavor, do_notify, res_type):
    location_info = flavor["properties"]["location_info"]
    vim_id, tenant_name = location_info["vimid"], location_info["tenant"]
    virtual_compute = flavor["virtual_compute"]
    virtual_storages = ignore_case_get(flavor, "virtual_storages")
    virtual_cpu = ignore_case_get(virtual_compute, "virtual_cpu")
    virtual_memory = ignore_case_get(virtual_compute, "virtual_memory")
    param = {
        "name": "Flavor_%s" % flavor["vdu_id"],
        "vcpu": int(ignore_case_get(virtual_cpu, "num_virtual_cpu")),
        "memory": int(ignore_case_get(virtual_memory, "virtual_mem_size").replace('MB', '').strip()),
        "isPublic": True
    }

    # Get flavor id from OOF
    vdu_id = ignore_case_get(flavor, "vdu_id", "")
    flavor_id = ""
    for one_vdu in location_info["vduInfo"]:
        if one_vdu["vduName"] == vdu_id:
            flavor_id = ignore_case_get(one_vdu, "flavorId", "")
            break

    # Add check if OOF return flavor id has value
    # If value is not None, we use it.
    # If value is None, we will create flavor again.
    if flavor_id:
        set_res_cache(res_cache, res_type, flavor["vdu_id"], flavor_id)
    else:
        if virtual_storages:
            for virtual_storage in virtual_storages:
                vs_id = virtual_storage["virtual_storage_id"]
                for vs in data["volume_storages"]:
                    if vs["volume_storage_id"] == vs_id:
                        disk_type = ignore_case_get(vs["properties"], "type_of_storage")
                        size_of_storage = ignore_case_get(vs["properties"], "size_of_storage")
                        disk_size = int(size_of_storage.replace('GB', '').replace('"', '').strip())
                        if disk_type == "root":
                            param["disk"] = disk_size
                        elif disk_type == "ephemeral":
                            param["ephemeral"] = disk_size
                        elif disk_type == "swap":
                            param["swap"] = disk_size
        else:
            virtual_storages = ignore_case_get(virtual_compute, "virtual_storages")
            size_of_storage = ignore_case_get(virtual_storages[0], "size_of_storage")
            disk_size = int(size_of_storage.replace('GB', '').replace('"', '').strip())
            param["disk"] = disk_size

        tenant_id = get_tenant_id(vim_cache, vim_id, tenant_name)
        logger.debug("param:%s" % param)
        ret = api.create_flavor(vim_id, tenant_id, param)
        logger.debug("hhb ret:%s" % ret)
        do_notify(res_type, ret)
        set_res_cache(res_cache, res_type, flavor["vdu_id"], ret["id"])


def create_vm(vim_cache, res_cache, data, vm, do_notify, res_type):
    location_info = vm["properties"]["location_info"]
    vim_id, tenant_name = location_info["vimid"], location_info["tenant"]
    tenant_id = get_tenant_id(vim_cache, vim_id, tenant_name)
    param = {
        "name": vm["properties"].get("name", "undefined"),
        "flavorId": get_res_id(res_cache, RES_FLAVOR, vm["vdu_id"]),
        "boot": {},
        "nicArray": [],
        "contextArray": [],
        "volumeArray": []
    }
    # set boot param
    if "artifacts" in vm and vm["artifacts"]:
        param["boot"]["type"] = BOOT_FROM_IMAGE
        img_name = ""
        for artifact in vm["artifacts"]:
            if artifact["artifact_name"] == "sw_image":
                # TODO: after DM define
                img_name = os.path.basename(artifact["file"])
                break
        if not img_name:
            raise VimException("Undefined image(%s)" % vm["artifacts"], ERR_CODE)
        images = api.list_image(vim_id, tenant_id)
        for image in images["images"]:
            if img_name == image["name"]:
                param["boot"]["imageId"] = image["id"]
                break
        if "imageId" not in param["boot"]:
            raise VimException("Undefined artifacts image(%s)" % vm["artifacts"], ERR_CODE)
    elif vm["virtual_storages"]:
        param["boot"]["type"] = BOOT_FROM_VOLUME
        vol_id = vm["virtual_storages"][0]["virtual_storage_id"]
        param["boot"]["volumeId"] = get_res_id(res_cache, RES_VOLUME, vol_id)
    else:
        raise VimException("No image and volume defined", ERR_CODE)

    for cp_id in ignore_case_get(vm, "cps"):
        param["nicArray"].append({
            "portId": get_res_id(res_cache, RES_PORT, cp_id)
        })
    param["contextArray"] = ignore_case_get(vm["properties"], "inject_files", [])
    logger.debug("contextArray:%s", param["contextArray"])
    for vol_data in ignore_case_get(vm, "volume_storages"):
        vol_id = vol_data["volume_storage_id"]
        param["volumeArray"].append({
            "volumeId": get_res_id(res_cache, RES_VOLUME, vol_id)
        })

    user_data = base64.b64encode(bytes(ignore_case_get(vm["properties"], "user_data"), "utf-8")).decode("utf-8")
    set_opt_val(param, "availabilityZone", ignore_case_get(location_info, "availability_zone"))
    set_opt_val(param, "userdata", user_data)
    set_opt_val(param, "metadata", ignore_case_get(vm["properties"], "meta_data"))
    set_opt_val(param, "securityGroups", "")   # TODO List of names of security group
    set_opt_val(param, "serverGroup", "")      # TODO the ServerGroup for anti-affinity and affinity

    ret = api.create_vm(vim_id, tenant_id, param)
    ret["ports"] = [nic.get("portId") for nic in param["nicArray"]]
    ret["vimId"] = vim_id
    ret["tenantId"] = tenant_id
    do_notify(res_type, ret)
    vm_id = ret["id"]
    if ignore_case_get(ret, "name"):
        vm_name = vm["properties"].get("name", "undefined")
        logger.debug("vm_name:%s" % vm_name)
    opt_vm_status = "Timeout"
    retry_count, max_retry_count = 0, 100
    while retry_count < max_retry_count:
        vm_info = api.get_vm(vim_id, tenant_id, vm_id)
        if vm_info["status"].upper() == "ACTIVE":
            logger.debug("Vm(%s) is active", vm_id)
            return
        if vm_info["status"].upper() == "ERROR":
            opt_vm_status = vm_info["status"]
            break
        time.sleep(2)
        retry_count = retry_count + 1
    raise VimException("Failed to create Vm(%s): %s." % (vm_name, opt_vm_status), ERR_CODE)


def list_port_of_vm(vim_cache, res_cache, data, port, do_notify, res_type):
    location_info = None
    vm_id = ignore_case_get(port, "vm_id")
    port_ref_vdu_id = ignore_case_get(port, "vdu_id")
    for vdu in ignore_case_get(data, "vdus"):
        if vdu["vdu_id"] == port_ref_vdu_id:
            location_info = vdu["properties"]["location_info"]
            if port["cp_id"] not in vdu["cps"]:
                vdu["cps"].append(port["cp_id"])
            break
    if not location_info:
        err_msg = "vdu_id(%s) for cp(%s) is not defined."
        raise VimException(err_msg % (port_ref_vdu_id, port["cp_id"]), ERR_CODE)

    vim_id, tenant_name = location_info["vimid"], location_info["tenant"]
    tenant_id = get_tenant_id(vim_cache, vim_id, tenant_name)
    ret = api.list_vm_port(vim_id, tenant_id, vm_id)
    ret["nodeId"] = port["cp_id"]
    do_notify(res_type, ret)
    set_res_cache(res_cache, res_type, port["cp_id"], ret["id"])

    return ret


def get_port_of_vm(vim_cache, res_cache, data, port, do_notify, res_type):
    location_info = None
    vm_id = ignore_case_get(port, "vm_id")
    port_id = ignore_case_get(port, "cp_id")
    port_ref_vdu_id = ignore_case_get(port, "vdu_id")
    for vdu in ignore_case_get(data, "vdus"):
        if vdu["vdu_id"] == port_ref_vdu_id:
            location_info = vdu["properties"]["location_info"]
            if port["cp_id"] not in vdu["cps"]:
                vdu["cps"].append(port["cp_id"])
            break
    if not location_info:
        err_msg = "vdu_id(%s) for cp(%s) is not defined."
        raise VimException(err_msg % (port_ref_vdu_id, port["cp_id"]), ERR_CODE)

    vim_id, tenant_name = location_info["vimid"], location_info["tenant"]
    tenant_id = get_tenant_id(vim_cache, vim_id, tenant_name)
    ret = api.get_vm_port(vim_id, tenant_id, vm_id, port_id)
    ret["nodeId"] = port["cp_id"]
    do_notify(res_type, ret)
    set_res_cache(res_cache, res_type, port["cp_id"], ret["id"])

    return ret


def create_port_of_vm(vim_cache, res_cache, data, port, do_notify, res_type):
    location_info = None
    vm_id = ignore_case_get(port, "vm_id")
    port_id = ignore_case_get(port, "port_id")
    port_ref_vdu_id = ignore_case_get(port, "vdu_id")
    for vdu in ignore_case_get(data, "vdus"):
        if vdu["vdu_id"] == port_ref_vdu_id:
            location_info = vdu["properties"]["location_info"]
            if port["cp_id"] not in vdu["cps"]:
                vdu["cps"].append(port["cp_id"])
            break
    if not location_info:
        err_msg = "vdu_id(%s) for cp(%s) is not defined."
        raise VimException(err_msg % (port_ref_vdu_id, port["cp_id"]), ERR_CODE)
    network_id = ignore_case_get(port, "networkId")
    # subnet_id = ignore_case_get(port, "subnetId")
    if not network_id:
        network_id = get_res_id(res_cache, RES_NETWORK, port["vl_id"])
    #    subnet_id = get_res_id(res_cache, RES_SUBNET, port["vl_id"])
    # param = {
    #     "networkId": network_id,
    #     "name": port["cp_id"]
    # }
    # set_opt_val(param, "subnetId", subnet_id)
    # set_opt_val(param, "macAddress", ignore_case_get(port["properties"], "mac_address"))
    # ip_address = []
    # for one_protocol_data in port["properties"]["protocol_data"]:
    #     l3_address_data = one_protocol_data["address_data"]["l3_address_data"]  # l3 is not 13
    #     fixed_ip_address = ignore_case_get(l3_address_data, "fixed_ip_address")
    #     ip_address.extend(fixed_ip_address)
    # for one_virtual_network_interface in port["properties"].get("virtual_network_interface_requirements", []):
    #     interfaceTypeString = one_virtual_network_interface["network_interface_requirements"]["interfaceType"]
    #     interfaceType = json.loads(interfaceTypeString)["configurationValue"]
    #     vnic_type = ignore_case_get(port["properties"], "vnic_type")
    #     if vnic_type == "":
    #         if interfaceType == "SR-IOV":
    #             set_opt_val(param, "vnicType", "direct")
    #     else:
    #         set_opt_val(param, "vnicType", vnic_type)
    #
    # set_opt_val(param, "ip", ",".join(ip_address))
    # set_opt_val(param, "securityGroups", "")  # TODO
    vim_id, tenant_name = location_info["vimid"], location_info["tenant"]
    tenant_id = get_tenant_id(vim_cache, vim_id, tenant_name)

    # ip_address = ignore_case_get(ignore_case_get(port, "properties"), "ip_address")
    param = {
        "interfaceAttachment": {
            "port_id": port_id
        }
    }
    ret = api.create_vm_port(vim_id, tenant_id, vm_id, param)
    ret["nodeId"] = port["cp_id"]
    do_notify("create", res_type, ret)


def delete_port_of_vm(vim_cache, res_cache, data, port, do_notify, res_type):
    location_info = None
    vm_id = ignore_case_get(port, "vm_id")
    port_id = ignore_case_get(port, "cp_id")
    port_ref_vdu_id = ignore_case_get(port, "vdu_id")
    for vdu in ignore_case_get(data, "vdus"):
        if vdu["vdu_id"] == port_ref_vdu_id:
            location_info = vdu["properties"]["location_info"]
            if port["cp_id"] not in vdu["cps"]:
                vdu["cps"].append(port["cp_id"])
            break
    if not location_info:
        err_msg = "vdu_id(%s) for cp(%s) is not defined."
        raise VimException(err_msg % (port_ref_vdu_id, port["cp_id"]), ERR_CODE)

    vim_id, tenant_name = location_info["vimid"], location_info["tenant"]
    tenant_id = get_tenant_id(vim_cache, vim_id, tenant_name)
    ret = api.delete_vm_port(vim_id, tenant_id, vm_id, port_id)
    ret["nodeId"] = port["cp_id"]
    do_notify("delete", res_type, port_id)
    set_res_cache(res_cache, res_type, port["cp_id"], ret["id"])
