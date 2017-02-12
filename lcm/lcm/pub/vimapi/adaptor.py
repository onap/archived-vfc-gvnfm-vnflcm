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

from lcm.pub.utils.values import ignore_case_get
from . import api
from .exceptions import VimException

logger = logging.getLogger(__name__)

RES_EXIST, RES_NEW = 0, 1
NET_PRIVATE, NET_SHSRED = 0, 1
VLAN_TRANSPARENT_NO, VLAN_TRANSPARENT_YES = 0, 1

def create_vim_res(data, do_notify, do_rollback):
    try:
        for vol in ignore_case_get(data, "volume_storages"):
            create_volume(vol, do_notify, 10)
        for network in ignore_case_get(data, "vls"):
            create_network(network, do_notify, 20)
            
    except VimException as e:
        logger.error(e.message)
        do_rollback(e.message)
    except:
        logger.error(traceback.format_exc())
        do_rollback(str(sys.exc_info()))
    
def create_volume(vol, do_notify, progress)
    param = {
        "tenant": vol["properties"]["location_info"]["tenant"],	
        "volumeName": vol["properties"]["volume_name"],	
        "volumeSize": int(ignore_case_get(vol["properties"], "size", "0")),
        "imageName": ignore_case_get(vol, "image_file"),
        "volumeType": ignore_case_get(vol["properties"], "custom_volume_type")
    }
    vim_id = vol["properties"]["location_info"]["vimid"],	
    ret = api.create_volume(vim_id, param)
    do_notify(progress, ret)
    
def create_network(network, do_notify, progress):
    param = {
        "tenant": network["properties"]["location_info"]["tenant"],	
        "networkName": network["properties"]["network_name"],
        "shared": NET_PRIVATE,
        "networkType": network["properties"]["network_type"],
        "physicalNetwork": ignore_case_get(network["properties"], "physical_network")
    }
    vlan_transparent = ignore_case_get(network["properties"], "vlan_transparent")
    if vlan_transparent:
        param["vlanTransparent"] = VLAN_TRANSPARENT_YES
    segmentation_id = ignore_case_get(network["properties"], "segmentation_id")
    if segmentation_id:
        param["segmentationId"] = int(segmentation_id)
    vim_id = network["properties"]["location_info"]["vimid"],
    ret = api.create_network(vim_id, param)
    do_notify(progress, ret)
    

