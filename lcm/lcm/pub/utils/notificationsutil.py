# Copyright (C) 2018 Verizon. All Rights Reserved
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

import requests
from requests.auth import HTTPBasicAuth
from rest_framework import status

from lcm.nf import const
from lcm.pub.database.models import SubscriptionModel
from lcm.pub.database.models import VmInstModel
from lcm.pub.database.models import NetworkInstModel
from lcm.pub.database.models import PortInstModel
from lcm.pub.database.models import StorageInstModel
from lcm.pub.database.models import VNFCInstModel
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.enumutil import enum

logger = logging.getLogger(__name__)

NOTIFY_TYPE = enum(
    lCM_OP_OCC="VnfLcmOperationOccurrenceNotification",
    CREATION="VnfIdentifierCreationNotification",
    DELETION="VnfIdentifierDeletionNotification"
)


class NotificationsUtil(object):
    def send_notification(self, notification):
        logger.info("Send Notifications to the callbackUri")
        filters = {
            "operationState": "operation_states",
            "operation": "operation_types"
        }
        subscriptions_filter = {v + "__contains": notification[k] for k, v in list(filters.items())}

        subscriptions = SubscriptionModel.objects.filter(**subscriptions_filter)
        if not subscriptions.exists():
            logger.info("No subscriptions created for the filters %s" % notification)
            return
        logger.info("Start sending notifications")
        for subscription in subscriptions:
            # set subscription id
            notification["subscriptionId"] = subscription.subscription_id
            notification['_links']['subscription'] = {
                'href': '/api/vnflcm/v1/subscriptions/%s' % subscription.subscription_id
            }
            callbackUri = subscription.callback_uri
            auth_info = json.loads(subscription.auth_info)
            if auth_info["authType"] != const.OAUTH2_CLIENT_CREDENTIALS:
                try:
                    self.post_notification(callbackUri, auth_info, notification)
                except Exception as e:
                    logger.error("Failed to post notification: %s", e.args[0])

    def post_notification(self, callbackUri, auth_info, notification):
        params = auth_info.get("paramsBasic", {})
        username = params.get("userName")
        password = params.get("password")
        logger.info("Sending notification to %s", callbackUri)
        resp = requests.post(
            callbackUri,
            data=notification,
            auth=HTTPBasicAuth(username, password)
        )
        if resp.status_code != status.HTTP_204_NO_CONTENT:
            logger.error("Notify %s failed: %s", callbackUri, resp.text)


def set_affected_vnfcs(affected_vnfcs, nfinstid, changetype):
    vnfcs = VNFCInstModel.objects.filter(instid=nfinstid)
    for vnfc in vnfcs:
        vm_resource = {}
        if vnfc.vmid:
            vm = VmInstModel.objects.filter(vmid=vnfc.vmid)
            if vm:
                vm_resource = {
                    'vimConnectionId': vm[0].vimid,
                    'resourceId': vm[0].resourceid,
                    'resourceProviderId': vm[0].vmname,  # TODO: is resourceName mapped to resourceProviderId?
                    'vimLevelResourceType': 'vm'
                }
        affected_vnfcs.append({
            'id': vnfc.vnfcinstanceid,
            'vduId': vnfc.vduid,
            'changeType': changetype,
            'computeResource': vm_resource
        })
    logger.debug("affected_vnfcs=%s", affected_vnfcs)
    return affected_vnfcs


def set_affected_vls(affected_vls, nfinstid, changetype):
    networks = NetworkInstModel.objects.filter(instid=nfinstid)
    for network in networks:
        network_resource = {
            'vimConnectionId': network.vimid,
            'resourceId': network.resourceid,
            'resourceProviderId': network.name,  # TODO: is resourceName mapped to resourceProviderId?
            'vimLevelResourceType': 'network'
        }
        affected_vls.append({
            'id': network.networkid,
            'virtualLinkDescId': network.nodeId,
            'changeType': changetype,
            'networkResource': network_resource
        })
    logger.debug("affected_vls=%s", affected_vls)


def set_ext_connectivity(ext_connectivity, nfinstid):
    ext_connectivity_map = {}
    ports = PortInstModel.objects.filter(instid=nfinstid)
    for port in ports:
        if port.networkid not in ext_connectivity_map:
            ext_connectivity_map[port.networkid] = []
        ext_connectivity_map[port.networkid].append({
            'id': port.portid,  # TODO: port.portid or port.nodeid?
            'resourceHandle': {
                'vimConnectionId': port.vimid,
                'resourceId': port.resourceid,
                'resourceProviderId': port.name,  # TODO: is resourceName mapped to resourceProviderId?
                'vimLevelResourceType': 'port'
            },
            'cpInstanceId': port.portid  # TODO: port.cpinstanceid is not initiated when create port resource.
        })
    for network_id, ext_link_ports in list(ext_connectivity_map.items()):
        networks = NetworkInstModel.objects.filter(networkid=network_id)
        net_name = networks[0].name if networks else network_id
        network_resource = {
            'vimConnectionId': ext_link_ports[0]['resourceHandle']['vimConnectionId'],
            'resourceId': network_id,
            'resourceProviderId': net_name,  # TODO: is resourceName mapped to resourceProviderId?
            'vimLevelResourceType': 'network'
        }
        ext_connectivity.append({
            'id': network_id,
            'resourceHandle': network_resource,
            'extLinkPorts': ext_link_ports
        })
    logger.debug("ext_connectivity=%s", ext_connectivity)


def set_affected_vss(affected_vss, nfinstid, changetype):
    vss = StorageInstModel.objects.filter(instid=nfinstid)
    for vs in vss:
        affected_vss.append({
            'id': vs.storageid,
            'virtualStorageDescId': vs.nodeId,
            'changeType': changetype,
            'storageResource': {
                'vimConnectionId': vs.vimid,
                'resourceId': vs.resourceid,
                'resourceProviderId': vs.name,  # TODO: is resourceName mapped to resourceProviderId?
                'vimLevelResourceType': 'volume'
            }
        })
    logger.debug("affected_vss=%s", affected_vss)


def get_notification_status(operation_state):
    if operation_state == const.OPERATION_STATE_TYPE.STARTING:
        return const.LCM_NOTIFICATION_STATUS.START
    return const.LCM_NOTIFICATION_STATUS.RESULT


def prepare_notification(nfinstid, jobid, operation, operation_state):
    logger.info('Start to prepare notification')
    notification_content = {
        'id': str(uuid.uuid4()),  # shall be the same if sent multiple times due to multiple subscriptions.
        'notificationType': NOTIFY_TYPE.lCM_OP_OCC,
        # set 'subscriptionId' after filtering for subscribers
        'timeStamp': now_time(),
        'notificationStatus': get_notification_status(operation_state),
        'operationState': operation_state,
        'vnfInstanceId': nfinstid,
        'operation': operation,
        'isAutomaticInvocation': False,
        'vnfLcmOpOccId': jobid,
        'affectedVnfcs': [],
        'affectedVirtualLinks': [],
        'affectedVirtualStorages': [],
        'changedExtConnectivity': [],
        'error': '',
        '_links': {
            'vnfInstance': {
                'href': '%s/vnf_instances/%s' % (const.URL_PREFIX, nfinstid)
            },
            'vnfLcmOpOcc': {
                'href': '%s/vnf_lcm_op_occs/%s' % (const.URL_PREFIX, jobid)
            }
        }
    }
    return notification_content


def prepare_notification_data(nfinstid, jobid, changetype, operation):
    data = prepare_notification(
        nfinstid=nfinstid,
        jobid=jobid,
        operation=operation,
        operation_state=const.OPERATION_STATE_TYPE.COMPLETED
    )

    set_affected_vnfcs(data['affectedVnfcs'], nfinstid, changetype)
    set_affected_vls(data['affectedVirtualLinks'], nfinstid, changetype)
    set_affected_vss(data['affectedVirtualStorages'], nfinstid, changetype)
    set_ext_connectivity(data['changedExtConnectivity'], nfinstid)

    logger.debug('Notification content: %s' % data)
    return data


def prepare_vnf_identifier_notification(notify_type, nfinstid):
    data = {
        "id": str(uuid.uuid4()),  # shall be the same if sent multiple times due to multiple subscriptions.
        "notificationType": notify_type,
        "timeStamp": now_time(),
        "vnfInstanceId": nfinstid,
        "_links": {
            "vnfInstance": {
                'href': '%s/vnf_instances/%s' % (const.URL_PREFIX, nfinstid)
            }
        }
    }

    logger.debug('Vnf Identifier Notification: %s' % data)
    return data
