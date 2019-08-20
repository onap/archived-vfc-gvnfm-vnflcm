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

from django.conf.urls import include, url
from django.contrib import admin

from lcm.pub.config.config import REG_TO_MSB_WHEN_START, REG_TO_MSB_REG_URL, REG_TO_MSB_REG_PARAM, \
    QRY_MSB_REG_URL, UNREG_MSB_URL


urlpatterns = [
    url(r'^api/vnflcm/v1/admin', admin.site.urls),
    url(r'^', include('lcm.samples.urls')),
    url(r'^', include('lcm.nf.urls')),
    # url(r'^', include('lcm.v2.urls')),
    url(r'^', include('lcm.jobs.urls')),
    url(r'^', include('lcm.swagger.urls')),
]

# regist to MSB when startup
if REG_TO_MSB_WHEN_START:
    import json
    from lcm.pub.utils.restcall import req_by_msb
    from lcm.pub.utils.values import ignore_case_get

    ret = req_by_msb(QRY_MSB_REG_URL, "GET")
    if ret[0] == 0:
        msbinfo = json.JSONDecoder().decode(ret[1])
        for node in ignore_case_get(msbinfo, "nodes"):
            req_by_msb(UNREG_MSB_URL % (node["ip"], node["port"]), "DELETE")

    req_by_msb(REG_TO_MSB_REG_URL, "POST", json.JSONEncoder().encode(REG_TO_MSB_REG_PARAM))
