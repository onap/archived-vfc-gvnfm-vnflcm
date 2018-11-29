# Copyright 2017 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import uuid

from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.restcall import req_by_msb
from lcm.pub.utils.timeutil import now_time
from lcm.pub.database.models import (
    NfInstModel, VmInstModel, NetworkInstModel,
    PortInstModel, StorageInstModel, VNFCInstModel
)

logger = logging.getLogger(__name__)


def get_packageinfo_by_vnfdid(vnfdid):
    ret = req_by_msb('api/gvnfmdriver/v1/vnfpackages', 'GET')
    if ret[0] != 0:
        logger.error('Status code is %s, detail is %s.', ret[2], ret[1])
        raise NFLCMException('Failed to query package_info of vnfdid(%s) from nslcm.' % vnfdid)
    return json.JSONDecoder().decode(ret[1])


def apply_grant_to_nfvo(data):
    ret = req_by_msb('api/gvnfmdriver/v1/resource/grant', 'PUT', data)
    if ret[0] != 0:
        logger.error('Status code is %s, detail is %s.', ret[2], ret[1])
        raise NFLCMException('Nf instancing apply grant exception')
    return json.JSONDecoder().decode(ret[1])


def notify_lcm_to_nfvo(data):
    ret = req_by_msb('api/gvnfmdriver/v1/vnfs/lifecyclechangesnotification', 'POST', data)
    if ret[0] != 0:
        logger.error('Status code is %s, detail is %s.', ret[2], ret[1])
        raise NFLCMException('Nf lcm notify exception')
    return ret[1]


def prepare_notification_data(nfinstid, jobid, changetype, operation):
    logger.info('Send notify request to nfvo')
    affected_vnfcs = []
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
    affected_vls = []
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
    ext_connectivity = []
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
            'cpInstanceId': port.cpinstanceid  # TODO: port.cpinstanceid is not initiated when create port resource.
        })
    for network_id, ext_link_ports in ext_connectivity_map.items():
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
    affected_vss = []
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
    notification_content = {
        'id': str(uuid.uuid4()),  # shall be the same if sent multiple times due to multiple subscriptions.
        'notificationType': 'VnfLcmOperationOccurrenceNotification',
        # set 'subscriptionId' after filtering for subscribers
        'timeStamp': now_time(),
        'notificationStatus': 'RESULT',
        'operationState': 'COMPLETED',
        'vnfInstanceId': nfinstid,
        'operation': operation,
        'isAutomaticInvocation': False,
        'vnfLcmOpOccId': jobid,
        'affectedVnfcs': affected_vnfcs,
        'affectedVirtualLinks': affected_vls,
        'affectedVirtualStorages': affected_vss,
        'changedExtConnectivity': ext_connectivity,
        '_links': {
            'vnfInstance': {'href': '/api/vnflcm/v1/vnf_instances/%s' % nfinstid},
            # set 'subscription' link after filtering for subscribers
            'vnfLcmOpOcc': {'href': '/api/vnflcm/v1/vnf_lcm_op_occs/%s' % jobid}
        }
    }
    nfInsts = NfInstModel.objects.filter(nfinstid=nfinstid)
    notification_content['vnfmInstId'] = nfInsts[0].vnfminstid if nfInsts[0].vnfminstid else '1'
    logger.info('Notify request data = %s' % notification_content)
    return notification_content
