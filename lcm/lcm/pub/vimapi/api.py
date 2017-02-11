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

from lcm.pub.utils.restcall import req_by_msb
from .exceptions import VimException

VIM_DRIVER_BASE_URL = "openoapi/vimdriver/v1"

def call(vim_id, res, method, data=''):
    url = "%/%s/%s" % (VIM_DRIVER_BASE_URL, vim_id, res)
    ret = req_by_msb(url, method, data)
    if ret[0] > 0:
        raise VimException(ret[1], ret[2])
    return json.JSONDecoder().decode(ret[1]) if ret[1] else {}

######################################################################

def create_image(vim_id, data):
    return call(vim_id, "images", "POST", data)

def delete_image(vim_id, image_id):
    return call(vim_id, "images/%s" % image_id, "DELETE")
    
def get_image(vim_id, image_id):
    return call(vim_id, "images/%s" % image_id, "GET")
    
def list_image(vim_id):
    return call(vim_id, "images", "GET")

######################################################################

def create_network(vim_id, data):
    return call(vim_id, "networks", "POST", data)

def delete_network(vim_id, network_id):
    return call(vim_id, "networks/%s" % network_id, "DELETE")
    
def get_network(vim_id, network_id):
    return call(vim_id, "networks/%s" % network_id, "GET")
    
def list_network(vim_id):
    return call(vim_id, "networks", "GET")

######################################################################

def create_subnet(vim_id, data):
    return call(vim_id, "subnets", "POST", data)

def delete_subnet(vim_id, subnet_id):
    return call(vim_id, "subnets/%s" % subnet_id, "DELETE")
    
def get_subnet(vim_id, subnet_id):
    return call(vim_id, "subnets/%s" % subnet_id, "GET")
    
def list_subnet(vim_id):
    return call(vim_id, "subnets", "GET")

######################################################################

def create_port(vim_id, data):
    return call(vim_id, "ports", "POST", data)

def delete_port(vim_id, port_id):
    return call(vim_id, "ports/%s" % port_id, "DELETE")
    
def get_port(vim_id, port_id):
    return call(vim_id, "ports/%s" % port_id, "GET")
    
def list_port(vim_id):
    return call(vim_id, "ports", "GET")

######################################################################

def create_flavor(vim_id, data):
    return call(vim_id, "flavors", "POST", data)

def delete_flavor(vim_id, flavor_id):
    return call(vim_id, "flavors/%s" % flavor_id, "DELETE")
    
def get_flavor(vim_id, flavor_id):
    return call(vim_id, "flavors/%s" % flavor_id, "GET")
    
def list_flavor(vim_id):
    return call(vim_id, "flavors", "GET")

######################################################################

def create_vm(vim_id, data):
    return call(vim_id, "vms", "POST", data)

def delete_vm(vim_id, vm_id):
    return call(vim_id, "vms/%s" % vm_id, "DELETE")
    
def get_vm(vim_id, vm_id):
    return call(vim_id, "vms/%s" % vm_id, "GET")
    
def list_vm(vim_id):
    return call(vim_id, "vms", "GET")

######################################################################

def create_volume(vim_id, data):
    return call(vim_id, "volumes", "POST", data)

def delete_volume(vim_id, volume_id):
    return call(vim_id, "volumes/%s" % volume_id, "DELETE")
    
def get_volume(vim_id, volume_id):
    return call(vim_id, "volumes/%s" % volume_id, "GET")
    
def list_volume(vim_id):
    return call(vim_id, "volumes", "GET")
