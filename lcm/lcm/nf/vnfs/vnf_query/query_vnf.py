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
    VmInstModel, VimModel, VimUserModel
from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)


class QueryVnf:
    def __init__(self, data, instanceid):
        self.vnf_inst_id = instanceid
        self.data = data
        pass

    def query_single_vnf(self):
        vnf_inst = NfInstModel.objects.filter(nfinstid=self.vnf_inst_id)
        if not vnf_inst.exists():
            raise NFLCMException('VnfInst(%s) does not exist' % self.vnf_inst_id)
        resp_data = self.fill_resp_data(vnf_inst[0])
        return resp_data

    def query_multi_vnf(self):
        pass

    def fill_resp_data(self, vnf):
        logger.info('Get the list of vloumes')
        storage_inst = StorageInstModel.objects.filter(instid=vnf.nfinstid)
        arr = []
        for s in storage_inst:
            storage = {
                "virtualStorageInstanceId": s.storageid,
                "storageResource": {
                    "vimId": s.vimid,
                    "resourceId": s.resouceid
                }
            }
            arr.append(storage)
        logger.info('Get the VLInstModel of list.')
        vl_inst = VLInstModel.objects.filter(ownerid=vnf.nfinstid)
        vl_arr = []
        for v in vl_inst:
            net = NetworkInstModel.objects.filter(networkid=v.relatednetworkid)
            if not net:
                raise NFLCMException('NetworkInst(%s) does not exist.' % v.relatednetworkid)
            v_dic = {
                "virtualLinkInstanceId": v.vlinstanceid,
                "virtualLinkDescId": v.vldid,
                "networkResource": {
                    "vimId": net[0].vimid,
                    "resourceId": net[0].resouceid
                }
            }
            vl_arr.append(v_dic)
        logger.info('Get VNFCInstModel of list.')
        vnfc_insts = VNFCInstModel.objects.filter(nfinstid=vnf.nfinstid)
        vnfc_arr = []
        for vnfc in vnfc_insts:
            vm = VmInstModel.objects.filter(vmid=vnfc.vmid)
            if not vm:
                raise NFLCMException('VmInst(%s) does not exist.' % vnfc.vmid)
            storage = StorageInstModel.objects.filter(ownerid=vm[0].vmid)
            if not storage:
                raise NFLCMException('StorageInst(%s) does not exist.' % vm[0].vmid)
            vnfc_dic = {
                "vnfcInstanceId": vnfc.vnfcinstanceid,
                "vduId": vnfc.vduid,
                "computeResource": {
                    "vimId": vm[0].vimid,
                    "resourceId": vm[0].resouceid
                },
                "storageResourceIds": [s.storageid for s in storage]
            }
            vnfc_arr.append(vnfc_dic)
        logger.info('Get the VimInstModel of list.')
        vms = VmInstModel.objects.filter(instid=vnf.nfinstid)
        vim_arr = []
        # The 'vimInfoId' and 'vimId' each value are same
        for vm in vms:
            vims = VimModel.objects.filter(vimid=vm.vimid)
            for vim in vims:
                vim_users = VimUserModel.objects.filter(vimid=vim.vimid)
                vim_dic = {
                    "vimInfoId": vim.vimid,
                    "vimId": vim.vimid,
                    "interfaceInfo": {
                        "vimType": vim.type,
                        "apiVersion": vim.version,
                        "protocolType": (vim.apiurl.split(':')[0] if vim.apiurl and vim.apiurl.index(':') else 'http')
                    },
                    "accessInfo": {
                        "tenant": (vim_users[0].defaulttenant if vim_users and vim_users[0].defaulttenant else ''),
                        "username": (vim_users[0].username if vim_users and vim_users[0].username else ''),
                        "password": (vim_users[0].password if vim_users and vim_users[0].password else '')
                    },
                    "interfaceEndpoint": vim.apiurl
                }
                vim_arr.append(vim_dic)

        resp_data = {
            "vnfInstanceId": vnf.nfinstid,
            "vnfInstanceName": vnf.nf_name,
            # "vnfInstanceDescription": vnf.nf_desc,
            "onboardedVnfPkgInfoId": vnf.package_id,
            # "vnfdId": vnf.vnfdid,
            "vnfdVersion": vnf.version,
            # "vnfSoftwareVersion": vnf.vnfSoftwareVersion,
            "vnfProvider": vnf.vendor,
            # "vnfProductName": vnf.producttype,
            # "vnfConfigurableProperties": {vnf.vnfConfigurableProperties},
            # "instantiationState": vnf.status,
            "instantiatedVnfInfo": {
                "flavourId": vnf.flavour_id,
                "vnfState": vnf.status,
                "scaleStatus": [],
                "extCpInfo": [],
                "extVirtualLink": [],
                "monitoringParameters": {},
                # "localizationLanguage": vnf.localizationLanguage,
                "vimInfo": vim_arr,
                "vnfcResourceInfo": vnfc_arr,
                "virtualLinkResourceInfo": vl_arr,
                "virtualStorageResourceInfo": arr
            },
            # "metadata": vnf.input_params,
            # "extensions": vnf.extension
        }
        return resp_data
