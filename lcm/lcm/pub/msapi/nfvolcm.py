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

from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.restcall import req_by_msb

logger = logging.getLogger(__name__)


#call gvnfm driver
def get_packageinfo_by_vnfdid(vnfdid):
    ret = req_by_msb("openoapi/nslcm/v1/vnfs/%s" % vnfdid, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Failed to query package_info of vnfdid(%s) from nslcm." % vnfdid)
    return json.JSONDecoder().decode(ret[1])

#call gvnfm driver
def vnfd_rawdata_get(vnfdid, data):
    ret = req_by_msb("openoapi/nslcm/v1/vnfs/%s" % vnfdid, "GET", data)
    return ret

#call gvnfm driver
def apply_grant_to_nfvo(data):
    ret = req_by_msb("openoapi/nslcm/v1/grantvnf" , "POST", data)
    return ret

#call gvnfm driver
def notify_lcm_to_nfvo(data, nf_inst_id):
    ret = req_by_msb("openoapi/nslcm/v1/vnfs/%s/Notify"%nf_inst_id, "POST", data)
    return ret

#call gvnfm driver
def apply_res_to_nfvo(data):
    ret = req_by_msb("openoapi/nslcm/v1/res" , "POST", data)
    return ret