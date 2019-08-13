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
import base64
import sys
import traceback
import logging
import urllib.request
import urllib.error
import urllib.parse
import uuid
import httplib2

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

rest_no_auth, rest_oneway_auth, rest_bothway_auth = 0, 1, 2
HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_202_ACCEPTED = '200', '201', '204', '202'
status_ok_list = [HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_202_ACCEPTED]
HTTP_404_NOTFOUND, HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED, HTTP_400_BADREQUEST = '404', '403', '401', '400'
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
            if const.BASIC in auth_info["authType"]:
                try:
                    self.post_notification(callbackUri, auth_info, notification)
                except Exception as e:
                    logger.error("Failed to post notification: %s", e.args[0])

    def post_notification(self, callbackUri, auth_info, notification):
        # params = auth_info.get("paramsBasic", {})
        logger.info("Sending notification to %s", callbackUri)
        resp = self.call_req(callbackUri, "", "", "POST", notification)
        if resp[0] != 0:
            logger.error('Status code is %s, detail is %s.', resp[2], resp[1])
        # resp = requests.post(
        #     callbackUri,
        #     data=notification,
        #     headers={'Content-Type': 'application/json'}
        #     # auth=HTTPBasicAuth(username, password)
        # )
        # if resp.status_code != status.HTTP_204_NO_CONTENT:
        #     logger.error("Notify %s failed: %s", callbackUri, resp.text)

    def call_req(self, full_url, user, passwd, method, content=''):
        callid = str(uuid.uuid1())
        logger.debug("[%s]call_req('%s','%s','%s',%s,'%s','%s')" % (
            callid, full_url, user, passwd, rest_no_auth, method, content))
        ret = None
        resp_Location = ''
        resp_status = ''
        try:
            headers = {'content-type': 'application/json', 'accept': 'application/json'}
            if user:
                headers['Authorization'] = 'Basic %s' % base64.b64encode(
                    bytes('%s:%s' % (user, passwd), "utf-8")).decode()
            ca_certs = None
            for retry_times in range(3):
                http = httplib2.Http(ca_certs=ca_certs, disable_ssl_certificate_validation=True)
                http.follow_all_redirects = True
                try:
                    resp, resp_content = http.request(full_url, method=method.upper(), body=content, headers=headers)
                    logger.info("resp=%s,resp_content=%s" % (resp, resp_content))
                    resp_status, resp_body = resp['status'], resp_content.decode('UTF-8')
                    resp_Location = resp.get('Location', "")
                    logger.debug("[%s][%d]status=%s,resp_body=%s)" % (callid, retry_times, resp_status, resp_body))
                    if resp_status in status_ok_list:
                        ret = [0, resp_body, resp_status, resp_Location]
                    else:
                        ret = [1, resp_body, resp_status, resp_Location]
                    break
                except Exception as ex:
                    if 'httplib.ResponseNotReady' in str(sys.exc_info()):
                        logger.debug("retry_times=%d", retry_times)
                        logger.error(traceback.format_exc())
                        ret = [1, "Unable to connect to %s" % full_url, resp_status, resp_Location]
                        continue
                    raise ex
        except urllib.error.URLError as err:
            ret = [2, str(err), resp_status, resp_Location]
        except Exception as ex:
            logger.error(traceback.format_exc())
            logger.error("[%s]ret=%s" % (callid, str(sys.exc_info())))
            res_info = str(sys.exc_info())
            if 'httplib.ResponseNotReady' in res_info:
                res_info = "The URL[%s] request failed or is not responding." % full_url
            ret = [3, res_info, resp_status, resp_Location]
        except:
            logger.error(traceback.format_exc())
            ret = [4, str(sys.exc_info()), resp_status, resp_Location]

        logger.debug("[%s]ret=%s" % (callid, str(ret)))
        return ret

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
