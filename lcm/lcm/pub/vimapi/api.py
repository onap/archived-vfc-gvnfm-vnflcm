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

import json
from multiprocessing import Lock

from lcm.pub.msapi.aai import delete_aai_flavor
from lcm.pub.utils.restcall import req_by_msb
from .exceptions import VimException

VIM_DRIVER_BASE_URL = "api/multicloud/v0"
MUTEX_NET = Lock()
MUTEX_SUBNET = Lock()


def call(vim_id, tenant_id, res, method, data=''):
    if data and not isinstance(data, (str, unicode)):
        data = json.JSONEncoder().encode(data)
    url_fmt = "{base_url}/{vim_id}{tenant_id}/{res}"
    url = url_fmt.format(base_url=VIM_DRIVER_BASE_URL,
                         vim_id=vim_id,
                         tenant_id="/" + tenant_id if tenant_id else "",
                         res=res)
    ret = req_by_msb(url, method, data)
    if ret[0] > 0:
        raise VimException(ret[1], ret[2])
    return json.JSONDecoder().decode(ret[1]) if ret[1] else {}

######################################################################


def create_image(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "images", "POST", data)


def delete_image(vim_id, tenant_id, image_id):
    return call(vim_id, tenant_id, "images/%s" % image_id, "DELETE")


def get_image(vim_id, tenant_id, image_id):
    return call(vim_id, tenant_id, "images/%s" % image_id, "GET")


def list_image(vim_id, tenant_id):
    return call(vim_id, tenant_id, "images", "GET")

######################################################################


def create_network(vim_id, tenant_id, data):
    with MUTEX_NET:
        return call(vim_id, tenant_id, "networks", "POST", data)


def delete_network(vim_id, tenant_id, network_id):
    return call(vim_id, tenant_id, "networks/%s" % network_id, "DELETE")


def get_network(vim_id, tenant_id, network_id):
    return call(vim_id, tenant_id, "networks/%s" % network_id, "GET")


def list_network(vim_id, tenant_id):
    return call(vim_id, tenant_id, "networks", "GET")

######################################################################


def create_subnet(vim_id, tenant_id, data):
    with MUTEX_SUBNET:
        return call(vim_id, tenant_id, "subnets", "POST", data)


def delete_subnet(vim_id, tenant_id, subnet_id):
    return call(vim_id, tenant_id, "subnets/%s" % subnet_id, "DELETE")


def get_subnet(vim_id, tenant_id, subnet_id):
    return call(vim_id, tenant_id, "subnets/%s" % subnet_id, "GET")


def list_subnet(vim_id, tenant_id):
    return call(vim_id, tenant_id, "subnets", "GET")

######################################################################


def create_port(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "ports", "POST", data)


def delete_port(vim_id, tenant_id, port_id):
    return call(vim_id, tenant_id, "ports/%s" % port_id, "DELETE")


def get_port(vim_id, tenant_id, port_id):
    return call(vim_id, tenant_id, "ports/%s" % port_id, "GET")


def list_port(vim_id, tenant_id):
    return call(vim_id, tenant_id, "ports", "GET")

######################################################################


def create_flavor(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "flavors", "POST", data)


def delete_flavor(vim_id, tenant_id, flavor_id):
    # first delete aai register info
    ret = delete_aai_flavor(vim_id, tenant_id, flavor_id)
    if ret:
        return call(vim_id, tenant_id, "flavors/%s" % flavor_id, "DELETE")


def get_flavor(vim_id, tenant_id, flavor_id):
    return call(vim_id, tenant_id, "flavors/%s" % flavor_id, "GET")


def list_flavor(vim_id, tenant_id):
    return call(vim_id, tenant_id, "flavors", "GET")

######################################################################


def create_vm(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "servers", "POST", data)


def delete_vm(vim_id, tenant_id, vm_id):
    return call(vim_id, tenant_id, "servers/%s" % vm_id, "DELETE")


def get_vm(vim_id, tenant_id, vm_id):
    return call(vim_id, tenant_id, "servers/%s" % vm_id, "GET")


def list_vm(vim_id, tenant_id):
    return call(vim_id, tenant_id, "servers", "GET")


# Used to start/stop/restart a vm
def action_vm(vim_id, tenant_id, vm_id, data):
    return call(vim_id, tenant_id, "servers/%s/action" % vm_id, "POST", data)

######################################################################


def create_volume(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "volumes", "POST", data)


def delete_volume(vim_id, tenant_id, volume_id):
    return call(vim_id, tenant_id, "volumes/%s" % volume_id, "DELETE")


def get_volume(vim_id, tenant_id, volume_id):
    return call(vim_id, tenant_id, "volumes/%s" % volume_id, "GET")


def list_volume(vim_id, tenant_id):
    return call(vim_id, tenant_id, "volumes", "GET")

######################################################################


def list_tenant(vim_id, tenant_name=""):
    res = "tenants"
    if tenant_name:
        res = "%s?name=%s" % (res, tenant_name)
    return call(vim_id, "", res, "GET")
