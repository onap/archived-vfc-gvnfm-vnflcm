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

import json
import logging
import traceback
from threading import Thread

from lcm.pub.database.models import NfInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.msapi.gvnfmdriver import prepare_notification_data
# from lcm.pub.msapi.gvnfmdriver import notify_lcm_to_nfvo
from lcm.pub.msapi.sdc_run_catalog import query_vnfpackage_by_id
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.notificationsutil import NotificationsUtil
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.vimapi import adaptor
from lcm.nf.biz.grant_vnf import grant_resource
from lcm.nf.const import CHANGE_TYPE, GRANT_TYPE, OPERATION_TYPE
from lcm.nf.biz import common

logger = logging.getLogger(__name__)


class InstantiateVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(InstantiateVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.vim_id = ignore_case_get(ignore_case_get(self.data, "additionalParams"), "vimId")
        self.grant_type = GRANT_TYPE.INSTANTIATE

    def run(self):
        try:
            self.inst_pre()
            self.apply_grant()
            self.create_res()
            self.lcm_notify()
            JobUtil.add_job_status(self.job_id, 100, "Instantiate Vnf success.")
        except NFLCMException as e:
            self.vnf_inst_failed_handle(e.message)
        except Exception as e:
            logger.error(e.message)
            logger.error(traceback.format_exc())
            self.vnf_inst_failed_handle('unexpected exception')

    def inst_pre(self):
        vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if not vnf_insts.exists():
            raise NFLCMException('VNF nf_inst_id is not exist.')

        if vnf_insts[0].status != 'NOT_INSTANTIATED':
            raise NFLCMException('VNF instantiationState is not NOT_INSTANTIATED.')

        JobUtil.add_job_status(self.job_id, 5, 'Get packageinfo by vnfd_id')
        self.vnfd_id = vnf_insts[0].vnfdid
        JobUtil.add_job_status(self.job_id, 10, 'Get vnf package info from catalog by csar_id')
        input_parameters = []
        inputs = ignore_case_get(self.data, "additionalParams")
        if inputs:
            if isinstance(inputs, (str, unicode)):
                inputs = json.loads(inputs)
            for key, val in inputs.items():
                input_parameters.append({"key": key, "value": val})
        vnf_package = query_vnfpackage_by_id(self.vnfd_id)
        pkg_info = ignore_case_get(vnf_package, "packageInfo")
        self.vnfd_info = json.loads(ignore_case_get(pkg_info, "vnfdModel"))

        self.update_cps()
        metadata = ignore_case_get(self.vnfd_info, "metadata")
        csar_id = ignore_case_get(metadata, "id")
        version = ignore_case_get(metadata, "vnfdVersion")
        vendor = ignore_case_get(metadata, "vendor")
        netype = ignore_case_get(metadata, "type")
        vnfsoftwareversion = ignore_case_get(metadata, "version")
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).\
            update(package_id=csar_id,
                   flavour_id=ignore_case_get(self.data, "flavourId"),
                   version=version,
                   vendor=vendor,
                   netype=netype,
                   vnfd_model=json.dumps(self.vnfd_info),
                   status='NOT_INSTANTIATED',
                   vnfdid=self.vnfd_id,
                   localizationLanguage=ignore_case_get(self.data, 'localizationLanguage'),
                   input_params=input_parameters,
                   vnfSoftwareVersion=vnfsoftwareversion,
                   lastuptime=now_time())

        logger.info("VimId = %s" % self.vim_id)
        '''
        is_exist = NfvoRegInfoModel.objects.filter(nfvoid=self.nf_inst_id).exists()
        if not is_exist:
            NfvoRegInfoModel.objects.create(
                nfvoid=self.nf_inst_id,
                vnfminstid=ignore_case_get(self.data, "vnfmId"),
                apiurl=self.vim_id)
        '''
        JobUtil.add_job_status(self.job_id, 15, 'Nf instancing pre-check finish')
        logger.info("Nf instancing pre-check finish")

    def apply_grant(self):
        vdus = ignore_case_get(self.vnfd_info, "vdus")
        apply_result = grant_resource(data=self.data, nf_inst_id=self.nf_inst_id, job_id=self.job_id,
                                      grant_type=self.grant_type, vdus=vdus)
        self.set_location(apply_result)

        logger.info('VnfdInfo = %s' % self.vnfd_info)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='INSTANTIATED', lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 20, 'Nf instancing apply grant finish')
        logger.info("Nf instancing apply grant finish")

    def create_res(self):
        logger.info("Create resource start")
        vim_cache, res_cache = {}, {}
        adaptor.create_vim_res(self.vnfd_info, self.do_notify, vim_cache=vim_cache, res_cache=res_cache)
        JobUtil.add_job_status(self.job_id, 70, '[NF instantiation] create resource finish')
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).\
            update(vimInfo=json.dumps(vim_cache),
                   resInfo=json.dumps(res_cache))
        logger.info("Create resource finish")

    def lcm_notify(self):
        notification_content = prepare_notification_data(self.nf_inst_id, self.job_id, CHANGE_TYPE.ADDED, OPERATION_TYPE.INSTANTIATE)
        logger.info('Notify request data = %s' % notification_content)
        # resp = notify_lcm_to_nfvo(json.dumps(notification_content))
        # logger.info('Lcm notify end, response %s' % resp)
        NotificationsUtil().send_notification(notification_content)

    def vnf_inst_failed_handle(self, error_msg):
        logger.error('VNF instantiation failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status='NOT_INSTANTIATED', lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, error_msg)

    def do_notify(self, res_type, ret):
        logger.info('Creating [%s] resource' % res_type)
        resource_save_method = getattr(common, res_type + '_save')
        resource_save_method(self.job_id, self.nf_inst_id, ret)

    def update_cps(self):
        for extlink in ignore_case_get(self.data, "extVirtualLinks"):
            for ext_cp in ignore_case_get(extlink, "extCps"):
                cpdid = ignore_case_get(ext_cp, "cpdId")
                for cp in ignore_case_get(self.vnfd_info, "cps"):
                    if cpdid == ignore_case_get(cp, "cp_id"):
                        cp["networkId"] = ignore_case_get(extlink, "resourceId")
                        cp["subnetId"] = ignore_case_get(extlink, "resourceSubnetId")
                        break

    def set_location(self, apply_result):
        vim_connections = ignore_case_get(apply_result, "vimConnections")
        vnfid = ignore_case_get(apply_result, "vnfInstanceId")
        vim_assets = ignore_case_get(apply_result, "vimAssets")
        access_info = ignore_case_get(vim_connections[0], "accessInfo")
        tenant = ignore_case_get(access_info, "tenant")
        vimid = ignore_case_get(vim_connections[0], "vimId")
        cloud_owner, cloud_regionid = vimid.split("_")
        vdu_info = []

        for flavor in ignore_case_get(vim_assets, "computeResourceFlavours"):
            oof_vimid = flavor["vimConnectionId"]
            if oof_vimid and oof_vimid != "none":
                vimid = oof_vimid
            vdu_info.append({"vduName": flavor["resourceProviderId"],
                             "flavorName": flavor["vimFlavourId"],
                             "vimid": vimid})

        for resource_type in ['vdus', 'vls', 'cps', 'volume_storages']:
            for resource in ignore_case_get(self.vnfd_info, resource_type):
                if "location_info" in resource["properties"]:
                    resource["properties"]["location_info"]["vimid"] = vimid
                    resource["properties"]["location_info"]["tenant"] = tenant
                    resource["properties"]["location_info"]["vnfId"] = vnfid
                    resource["properties"]["location_info"]["cloudOwner"] = cloud_owner
                    resource["properties"]["location_info"]["cloudRegionId"] = cloud_regionid
                    resource["properties"]["location_info"]["vduInfo"] = vdu_info
                else:
                    resource["properties"]["location_info"] = {
                        "vimid": vimid,
                        "tenant": tenant,
                        "vnfId": vnfid,
                        "cloudOwner": cloud_owner,
                        "cloudRegionId": cloud_regionid,
                        "vduInfo": vdu_info}

    '''
    def get_subnet_ids(self, ext_cp):
        subnet_ids = []
        for cp_conf in ignore_case_get(ext_cp, "cpConfig"):
            for cp_protocol in ignore_case_get(ext_cp, "cpProtocolData"):
                ip_over_ethernet = ignore_case_get(cp_protocol, "ipOverEthernet")
                for ip_address in ignore_case_get(ip_over_ethernet, "ipAddresses"):
                    subnet_ids.append(ignore_case_get(ip_address, "subnetId"))
        return subnet_ids
    '''
