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

import logging

from lcm.pub.database.models import NfInstModel
from lcm.pub.database.models import StorageInstModel
from lcm.pub.database.models import VLInstModel
from lcm.pub.database.models import NetworkInstModel
from lcm.pub.database.models import VNFCInstModel
from lcm.pub.database.models import VmInstModel
from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)


class QueryVnf:
    def __init__(self, data, instanceid=''):
        self.vnf_inst_id = instanceid
        self.data = data

    def query_single_vnf(self):
        vnf_inst = NfInstModel.objects.filter(nfinstid=self.vnf_inst_id)
        if not vnf_inst.exists():
            raise NFLCMException('VnfInst(%s) does not exist.' % self.vnf_inst_id)
        return self.fill_resp_data(vnf_inst[0])

    def query_multi_vnf(self):
        vnf_insts = NfInstModel.objects.all()
        return [self.fill_resp_data(vnf_inst) for vnf_inst in vnf_insts]

    def fill_resp_data(self, vnf):
        logger.info('Get storages')
        storage_inst = StorageInstModel.objects.filter(instid=vnf.nfinstid)
        arr = []
        for s in storage_inst:
            storage = {
                "id": s.storageid,
                "storageResource": {
                    "vimConnectionId": s.vimid,
                    "resourceId": s.resourceid
                }
            }
            arr.append(storage)

        logger.info('Get networks')
        vl_inst = VLInstModel.objects.filter(ownerid=vnf.nfinstid)
        vl_arr = []
        for v in vl_inst:
            net = NetworkInstModel.objects.filter(networkid=v.relatednetworkid)
            if not net:
                raise NFLCMException('NetworkInst(%s) does not exist.' % v.relatednetworkid)
            v_dic = {
                "id": v.vlinstanceid,
                "virtualLinkDescId": v.vldid,
                "networkResource": {
                    "vimConnectionId": net[0].vimid,
                    "resourceId": net[0].resourceid
                }
            }
            vl_arr.append(v_dic)

        logger.info('Get vnfcs')
        vnfc_insts = VNFCInstModel.objects.filter(instid=vnf.nfinstid)
        vnfc_arr = []
        for vnfc in vnfc_insts:
            vm = VmInstModel.objects.filter(vmid=vnfc.vmid)
            if not vm:
                raise NFLCMException('VmInst(%s) does not exist.' % vnfc.vmid)
            if vm[0].volume_array:
                storage = StorageInstModel.objects.filter(resourceid__in=vm[0].volume_array)
            else:
                storage = []
            vnfc_dic = {
                "id": vnfc.vnfcinstanceid,
                "vduId": vnfc.vduid,
                "computeResource": {
                    "vimConnectionId": vm[0].vimid,
                    "resourceId": vm[0].resourceid
                },
                "storageResourceIds": [s.storageid for s in storage]
            }
            vnfc_arr.append(vnfc_dic)

        resp_data = {
            "id": vnf.nfinstid,
            "vnfInstanceName": vnf.nf_name,
            "vnfInstanceDescription": vnf.nf_desc,
            "vnfdId": vnf.vnfdid,
            "vnfProvider": vnf.vendor,
            "vnfProductName": vnf.netype,
            "vnfSoftwareVersion": vnf.vnfSoftwareVersion,
            "vnfdVersion": vnf.version,
            "vnfPkgId": vnf.package_id,
            "instantiationState": vnf.status,
            "instantiatedVnfInfo": {
                "flavourId": vnf.flavour_id,
                "vnfState": "STARTED",
                "scaleStatus": [],
                "extCpInfo": [],
                "extVirtualLinkInfo": [],
                "monitoringParameters": [],
                "vnfcResourceInfo": vnfc_arr,
                "vnfVirtualLinkResourceInfo": vl_arr,
                "virtualStorageResourceInfo": arr
            }
        }
        logger.debug("vnf instance: %s", resp_data)
        return resp_data
