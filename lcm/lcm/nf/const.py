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

from lcm.pub.config import config
from lcm.pub.utils.jobutil import enum

HEAL_ACTION_TYPE = enum(
    START="vmCreate",
    RESTART="vmReset"
)

ACTION_TYPE = enum(
    START=1,
    STOP=2,
    REBOOT=3
)

GRANT_TYPE = enum(
    INSTANTIATE="INSTANTIATE",
    TERMINATE="TERMINATE",
    HEAL_CREATE="Heal Create",
    HEAL_RESTART="Heal Restart",
    SCALE_IN="SCALE_IN",
    SCALE_OUT="SCALE_OUT",
    CHANGE_FLAVOUR="CHANGE_FLAVOUR",
    OPERATE="OPERATE",
    CHANGE_CONNECTIVITY="CHANGE_CONNECTIVITY",
)

VNF_STATUS = enum(
    NULL='null',
    INSTANTIATING="instantiating",
    INACTIVE='inactive',
    ACTIVE="active",
    FAILED="failed",
    TERMINATING="terminating",
    SCALING="scaling",
    OPERATING="operating",
    UPDATING="updating",
    HEALING="healing"
)

OPERATION_TYPE = enum(
    INSTANTIATE="INSTANTIATE",
    SCALE="SCALE",
    SCALE_TO_LEVEL="SCALE_TO_LEVEL",
    CHANGE_FLAVOUR="CHANGE_FLAVOUR",
    TERMINATE="TERMINATE",
    HEAL="HEAL",
    OPERATE="OPERATE",
    CHANGE_EXT_CONN="CHANGE_EXT_CONN",
    MODIFY_INFO="MODIFY_INFO"
)

OPERATION_TASK = enum(
    MODIFY="",
    INSTANTIATE="instantiate",
    SCALE="scale",
    SCALE_TO_LEVEL="scale_to_level",
    CHANGE_FLAVOUR="change_flavour",
    OPERATE="operate",
    HEAL="heal",
    CHANGE_EXT_CONN="change_ext_conn",
    TERMINATE="terminate"
)

SUB_OPERATION_TASK = enum(
    RETRY="retry",
    ROLLBACK="rollback",
    FAIL="fail",
    CANCEL="cancel",
    ERROR="error",
    SUCCESS="success",
    GRANTED="granted",
    UNRESOLVABLE_ERROR="unresolvable_error",
    AUTO_ROLLBACK="auto_rollback",
)

SUB_OPERATION_TUPLE = (
    SUB_OPERATION_TASK.RETRY,
    SUB_OPERATION_TASK.ROLLBACK,
    SUB_OPERATION_TASK.FAIL,
    SUB_OPERATION_TASK.CANCEL
)

INSTANTIATION_STATE = enum(
    NOT_INSTANTIATED="NOT_INSTANTIATED",
    INSTANTIATED="INSTANTIATED"
)

LCM_NOTIFICATION_STATUS = enum(START="START", RESULT="RESULT")

OPERATION_STATE_TYPE = enum(
    STARTING="STARTING",
    PROCESSING="PROCESSING",
    COMPLETED="COMPLETED",
    FAILED_TEMP="FAILED_TEMP",
    FAILED="FAILED",
    ROLLING_BACK="ROLLING_BACK",
    ROLLED_BACK="ROLLED_BACK"
)

RESULT_RANGE = (
    OPERATION_STATE_TYPE.COMPLETED,
    OPERATION_STATE_TYPE.FAILED_TEMP,
    OPERATION_STATE_TYPE.FAILED,
    OPERATION_STATE_TYPE.ROLLED_BACK
)

RUNNING_RANGE = (
    OPERATION_STATE_TYPE.STARTING,
    OPERATION_STATE_TYPE.PROCESSING,
    OPERATION_STATE_TYPE.ROLLING_BACK
)

FINAL_STATE_RANGE = (
    OPERATION_STATE_TYPE.COMPLETED,
    OPERATION_STATE_TYPE.FAILED,
    OPERATION_STATE_TYPE.ROLLED_BACK
)

CHANGE_TYPE = enum(
    ADDED='ADDED',
    REMOVED='REMOVED',
    MODIFIED='MODIFIED',
    TEMPORARY='TEMPORARY',
    LINK_PORT_ADDED='LINK_PORT_ADDED',
    LINK_PORT_REMOVED='LINK_PORT_REMOVED'
)

RESOURCE_MAP = {'Storage': 'volumn', 'Network': 'network', 'SubNetwork': 'subnet', 'Port': 'port',
                'Flavour': 'flavor', 'Vm': 'vm'}

URL_PREFIX = "http://%s:%s/api/vnflcm/v1" % (config.MSB_SERVICE_IP, config.MSB_SERVICE_PORT)

ROOT_URI = "api/vnflcm/v1/subscriptions/"

AUTH_TYPES = ["BASIC", "OAUTH2_CLIENT_CREDENTIALS", "TLS_CERT"]

BASIC = "BASIC"

OAUTH2_CLIENT_CREDENTIALS = "OAUTH2_CLIENT_CREDENTIALS"

LCCNNOTIFICATION = "VnfLcmOperationOccurrenceNotification"

NOTIFICATION_TYPES = [
    "VnfLcmOperationOccurrenceNotification",
    "VnfIdentifierCreationNotification",
    "VnfIdentifierDeletionNotification"
]

LCM_OPERATION_TYPES = [
    OPERATION_TYPE.INSTANTIATE,
    OPERATION_TYPE.SCALE,
    OPERATION_TYPE.SCALE_TO_LEVEL,
    OPERATION_TYPE.CHANGE_FLAVOUR,
    OPERATION_TYPE.TERMINATE,
    OPERATION_TYPE.HEAL,
    OPERATION_TYPE.OPERATE,
    OPERATION_TYPE.CHANGE_EXT_CONN,
    OPERATION_TYPE.MODIFY_INFO
]

LCM_OPERATION_STATE_TYPES = [
    OPERATION_STATE_TYPE.STARTING,
    OPERATION_STATE_TYPE.PROCESSING,
    OPERATION_STATE_TYPE.COMPLETED,
    OPERATION_STATE_TYPE.FAILED_TEMP,
    OPERATION_STATE_TYPE.FAILED,
    OPERATION_STATE_TYPE.ROLLING_BACK,
    OPERATION_STATE_TYPE.ROLLED_BACK
]
