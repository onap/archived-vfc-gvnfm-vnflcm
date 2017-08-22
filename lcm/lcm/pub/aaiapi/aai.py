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
import logging

from lcm.pub.config.config import AAI_BASE_URL, AAI_USER, AAI_PASSWORD
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.restcall import rest_no_auth, call_req_aai

logger = logging.getLogger(__name__)

def call_aai(full_url, method, req_data):
    pass

def create_ns(ns_id, data):
    resource = "/service-design-and-creation/services/service/%s" % ns_id
    ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Nf instancing apply grant exception")
    return json.JSONDecoder().decode(ret[1])

def create_vnf(vnf_id, data):
    # full_url = AAI_BASE_URL + "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    pass

def create_vserver(vserver_id, data):
    pass