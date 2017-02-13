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
import json
import traceback
import sys

from lcm.pub.utils.values import ignore_case_get, set_opt_val
from . import api
from .exceptions import VimException

logger = logging.getLogger(__name__)

RES_EXIST, RES_NEW = 0, 1
NET_PRIVATE, NET_SHSRED = 0, 1
VLAN_TRANSPARENT_NO, VLAN_TRANSPARENT_YES = 0, 1
IP_V4, IP_V6 = 4, 6
DHCP_DISABLED, DHCP_ENABLED = 0, 1
RES_VOLUME, RES_NETWORK, RES_SUBNET, RES_PORT, RES_FLAVOR, RES_VM = range(6)

def create_vim_res(data, do_notify, do_rollback):
    try:
        for vol in ignore_case_get(data, "volume_storages"):
            create_volume(vol, do_notify, 10)
        for network in ignore_case_get(data, "vls"):
            create_network(network, do_notify, 20)
        for subnet in ignore_case_get(data, "vls"):
            create_subnet(subnet, do_notify, 30)
            
            
    except VimException as e:
        logger.error(e.message)
        do_rollback(e.message)
    except:
        logger.error(traceback.format_exc())
        do_rollback(str(sys.exc_info()))
    
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
    do_notify(RES_VOLUME, progress, ret)
    
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
    do_notify(RES_NETWORK, progress, ret)
    
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
    vim_id = network["properties"]["location_info"]["vimid"],
    ret = api.create_subnet(vim_id, param)
    do_notify(RES_SUBNET, progress, ret)
    
