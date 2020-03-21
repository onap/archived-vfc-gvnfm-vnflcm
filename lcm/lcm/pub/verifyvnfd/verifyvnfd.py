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
import re
import os
import six
import logging
import jsonschema
from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)


def _format_validation_error(error):
    """
    :param error: validation error to format
    :type error: jsonchema.exceptions.ValidationError
    :returns: string representation of the validation error
    :rtype: str
    """
    match = re.search("(.+) is a required property", error.message)
    if match:
        message = 'Error: missing required property {}.'.format(
            match.group(1))
    else:
        message = 'Error: {}\n'.format(error.message)
        if len(error.absolute_path) > 0:
            message += 'Path: {}\n'.format(
                       '.'.join(
                           [six.text_type(path)
                            for path in error.absolute_path]))
        message += 'Value: {}'.format(json.dumps(error.instance))

    return message


def verify(new_vnfd):
    errors_found = []
    vnfd_schema_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "vnf_vnfd_all_schema.json")
    with open(vnfd_schema_path, "r") as fvnfd_schema:
        vnfd_schema = json.load(fvnfd_schema)
        vnfd_validator = jsonschema.validators.Draft4Validator(schema=vnfd_schema)
        for error in vnfd_validator.iter_errors(new_vnfd):
            # print("Error:%s" % error)
            logger.debug("vnfd verify fail,%s" % _format_validation_error(error))
            errors_found.append(_format_validation_error(error))
    if len(errors_found) > 0:
        raise NFLCMException(errors_found)
    return True
