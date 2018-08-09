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

from lcm.pub.database.models import NfInstModel, StorageInstModel, VLInstModel, NetworkInstModel, VNFCInstModel, \
    VmInstModel
from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)


class QueryVnf:
    def __init__(self, data, instanceid=''):
        self.vnf_inst_id = instanceid
        self.data = data

    def query_single_vnf(self):
        vnf_inst = NfInstModel.objects.filter(nfinstid=self.vnf_inst_id)
        if not vnf_inst.exists():
            raise NFLCMException('VnfInst(%s) does not exist' % self.vnf_inst_id)
        resp_data = self.fill_resp_data(vnf_inst[0])
        return resp_data

    def query_multi_vnf(self):
        vnf_insts = NfInstModel.objects.all()
        if not vnf_insts:
            raise NFLCMException('VnfInsts does not exist')
        resp_data = []
        for vnf_inst in vnf_insts:
            resp_data.append(self.fill_resp_data(vnf_inst))
        return resp_data

    def fill_resp_data(self, vnf):
        logger.info('Get storages')
        storage_inst = StorageInstModel.objects.filter(instid=vnf.nfinstid)
        arr = []
        for s in storage_inst:
            storage = {
                "id": s.storageid,
                "storageResource": {
                    "vimConnectionId": s.vimid,
                    "resourceId": s.resouceid
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
                    "resourceId": net[0].resouceid
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
            storage = StorageInstModel.objects.filter(ownerid=vm[0].vmid)
            if not storage:
                raise NFLCMException('StorageInst(%s) does not exist.' % vm[0].vmid)
            vnfc_dic = {
                "id": vnfc.vnfcinstanceid,
                "vduId": vnfc.vduid,
                "computeResource": {
                    "vimConnectionId": vm[0].vimid,
                    "resourceId": vm[0].resouceid
                },
                "storageResourceIds": [s.storageid for s in storage]
            }
            vnfc_arr.append(vnfc_dic)
        logger.info('Get vms')

        resp_data = {
            "id": vnf.nfinstid,
            "vnfInstanceName": vnf.nf_name,
            "vnfPkgId": vnf.package_id,
            "vnfdVersion": vnf.version,
            "vnfProvider": vnf.vendor,
            "instantiationState": vnf.status,
            "instantiatedVnfInfo": {
                "flavourId": vnf.flavour_id,
                "vnfState": "STARTED",
                "scaleStatus": [],
                "extCpInfo": [],
                "extVirtualLinkInfo": [],
                "monitoringParameters": {},
                "vnfcResourceInfo": vnfc_arr,
                "vnfVirtualLinkResourceInfo": vl_arr,
                "virtualStorageResourceInfo": arr
            }
        }
        return resp_data
