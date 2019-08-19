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
import os
import logging
import jsonschema
from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)


def verify(new_vnfd):
    errors_found = []
    vnfd_schema_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "vnf_vnfd_schema.json")
    with open(vnfd_schema_path, "r") as fvnfd_schema:
        vnfd_schema = json.load(fvnfd_schema)
        vnfd_validator = jsonschema.validators.Draft4Validator(schema=vnfd_schema)
        for error in vnfd_validator.iter_errors(new_vnfd):
            logger.error("vnfd verify fail:%s" % error)
            errors_found.append(error)
        if len(errors_found) > 0:
            raise NFLCMException(errors_found)
        return errors_found



