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

#call gvnfm driver
def vnfd_rawdata_get(vnfdid):
    ret = req_by_msb("openoapi/nslcm/v1/vnfs/%s" % vnfdid, "GET")
    return ret

#call gvnfm driver
def apply_grant_to_nfvo(data):
    ret = req_by_msb("openoapi/nslcm/v1/grantvnf" , "POST", data)
    return ret

#call gvnfm driver
def notify_lcm_to_nfvo(data, nf_inst_id):
    ret = req_by_msb("openoapi/nslcm/v1/vnfs/%s/Notify"%nf_inst_id, "POST", data)
    return ret