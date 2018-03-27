# Copyright 2016 ZTE Corporation.
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
import uuid

from lcm.pub.config.config import AAI_BASE_URL, AAI_USER, AAI_PASSWD
from lcm.pub.utils import restcall
logger = logging.getLogger(__name__)


def call_aai(resource, method, content=''):
    additional_headers = {
        'X-FromAppId': 'VFC-CATALOG',
        'X-TransactionId': str(uuid.uuid1())
    }
    return restcall.call_req(AAI_BASE_URL,
                             AAI_USER,
                             AAI_PASSWD,
                             restcall.rest_no_auth,
                             resource,
                             method,
                             content,
                             additional_headers)


def split_vim_to_owner_region(vim_id):
    split_vim = vim_id.split('_')
    cloud_owner = split_vim[0]
    cloud_region = "".join(split_vim[1:])
    return cloud_owner, cloud_region


def get_flavor_info(vim_id):
    cloud_owner, cloud_region = split_vim_to_owner_region(vim_id)
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/%s/flavors?depth=all" % \
               (cloud_owner, cloud_region)

    ret = call_aai(resource, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])

    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1]
