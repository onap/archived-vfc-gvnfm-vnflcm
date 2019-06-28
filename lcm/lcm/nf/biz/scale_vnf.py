# Copyright (C) 2018 Verizon. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import logging
import uuid
import traceback
from threading import Thread

from lcm.nf.biz import common
from lcm.nf.biz.grant_vnf import grant_resource
from lcm.nf.const import GRANT_TYPE, CHANGE_TYPE
from lcm.nf.const import RESOURCE_MAP, OPERATION_STATE_TYPE
from lcm.nf.const import INSTANTIATION_STATE
from lcm.nf.const import OPERATION_TYPE
from lcm.nf.const import OPERATION_TASK
from lcm.pub.database.models import NfInstModel
from lcm.pub.database.models import VNFCInstModel, PortInstModel
from lcm.pub.database.models import VmInstModel
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.notificationsutil import NotificationsUtil, prepare_notification
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.vimapi import adaptor
from .operate_vnf_lcm_op_occ import VnfLcmOpOcc

logger = logging.getLogger(__name__)

DEFAULT_STEPS = 1


class ScaleVnf(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(ScaleVnf, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.vnf_insts = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        self.lcm_op_occ = VnfLcmOpOcc(
            vnf_inst_id=nf_inst_id,
            lcm_op_id=job_id,
            operation=OPERATION_TYPE.SCALE,
            task=OPERATION_TASK.SCALE
        )
        self.op_type = OPERATION_TYPE.SCALE

    def run(self):
        try:
            self.scale_pre()
            self.lcm_op_occ.notify_lcm(OPERATION_STATE_TYPE.STARTING)
            JobUtil.add_job_status(self.job_id,
                                   50,
                                   "Start to apply grant.")
            self.apply_grant()
            self.lcm_op_occ.notify_lcm(OPERATION_STATE_TYPE.PROCESSING)
            JobUtil.add_job_status(self.job_id,
                                   75,
                                   "Start to scale Vnf.")
            self.do_operation()
            self.send_notification()
            JobUtil.add_job_status(self.job_id,
                                   100,
                                   "Scale Vnf success.")
            self.vnf_insts.update(status=INSTANTIATION_STATE.INSTANTIATED,
                                  lastuptime=now_time())
        except NFLCMException as e:
            logger.error(e.args[0])
            self.vnf_scale_failed_handle(e.args[0])
        except Exception as e:
            logger.error(e.args[0])
            logger.error(traceback.format_exc())
            self.vnf_scale_failed_handle(e.args[0])

    def scale_pre(self):
        self.scale_type = self.data.get("type")
        self.aspect_id = self.data.get("aspectId")
        self.number_of_steps = int(self.data.get("numberOfSteps", DEFAULT_STEPS))
        self.additional_params = self.data.get("additionalParams", {})
        self.is_scale_in = (self.scale_type == GRANT_TYPE.SCALE_IN)
        self.vnfd_info = json.loads(self.vnf_insts[0].vnfd_model)
        self.step_delta = self.get_scale_step_delta()
        self.target_vdu, self.step_inst_num = self.get_vdu_scale_aspect_deltas()
        self.scale_inst_num = self.number_of_steps * self.step_inst_num
        self.min_instance_num, self.max_instance_num = self.get_instance_range()
        self.check_if_can_scale()
        self.scale_out_resource = {}

    def apply_grant(self):
        logger.debug("Start scale apply grant")
        vdus = ignore_case_get(self.vnfd_info, "vdus")
        scale_vdus = [vdu for vdu in vdus if vdu["vdu_id"] == self.target_vdu]
        scale_vdus = scale_vdus * self.scale_inst_num
        grant_result = grant_resource(data=self.data,
                                      nf_inst_id=self.nf_inst_id,
                                      job_id=self.job_id,
                                      grant_type=self.scale_type,
                                      vdus=scale_vdus)
        logger.debug("Scale Grant result: %s", grant_result)
        self.set_location(grant_result)

    def do_operation(self):
        logger.debug("Start %s VNF resource", self.scale_type)
        logger.debug('VnfdInfo = %s' % self.vnfd_info)

        if self.is_scale_in:
            self.affected_vnfcs = []
            self.scale_in_resource = self.get_scale_in_resource(self.affected_vnfcs)
            adaptor.delete_vim_res(self.scale_in_resource, self.do_notify_del_vim_res)
        else:
            self.scale_out_resource = {
                'volumn': [],
                'network': [],
                'subnet': [],
                'port': [],
                'flavor': [],
                'vm': []
            }
            self.vnfd_info["volume_storages"] = []
            self.vnfd_info["vls"] = []
            self.vnfd_info["cps"] = self.vnfd_info["cps"] * self.scale_inst_num
            for cp in self.vnfd_info["cps"]:
                # TODO: how to set name for scale_out cp
                cp["properties"]["name"] = cp["cp_id"] + str(uuid.uuid4())
                cp_inst = PortInstModel.objects.filter(name__startswith=cp["cp_id"]).first()
                if cp_inst:
                    cp["networkId"] = cp_inst.networkid
                    cp["subnetId"] = cp_inst.subnetworkid
                else:
                    raise NFLCMException("CP(%s) does not exist" % cp["cp_id"])
            self.vnfd_info["vdus"] = self.vnfd_info["vdus"] * self.scale_inst_num
            for vdu in self.vnfd_info["vdus"]:
                # TODO: how to set name for scale_out vdu
                vdu["properties"]["name"] = vdu["properties"]["name"] + str(uuid.uuid4())

            vim_cache = json.loads(self.vnf_insts[0].vimInfo)
            res_cache = json.loads(self.vnf_insts[0].resInfo)
            adaptor.create_vim_res(self.vnfd_info,
                                   self.do_notify_create_vim_res,
                                   vim_cache=vim_cache,
                                   res_cache=res_cache)
            self.vnf_insts.update(vimInfo=json.dumps(vim_cache),
                                  resInfo=json.dumps(res_cache))
        logger.debug("%s VNF resource finish", self.scale_type)

    def send_notification(self):
        data = prepare_notification(nfinstid=self.nf_inst_id,
                                    jobid=self.job_id,
                                    operation=self.op_type,
                                    operation_state=OPERATION_STATE_TYPE.COMPLETED)

        # TODO: need set changedExtConnectivity for data
        if self.is_scale_in:
            data["affectedVnfcs"] = self.affected_vnfcs
        else:
            for vm in self.scale_out_resource["vm"]:
                self.set_affected_vnfcs(data["affectedVnfcs"], vm["res_id"])

        logger.debug('Notify request data = %s' % data)
        NotificationsUtil().send_notification(data)

    def rollback_operation(self):
        if self.is_scale_in:
            # SCALE_IN operaion does not support rollback
            return
        adaptor.delete_vim_res(self.scale_out_resource, self.do_notify_del_vim_res)

    def set_location(self, grant_result):
        vim_connections = ignore_case_get(grant_result, "vimConnections")
        access_info = ignore_case_get(vim_connections[0], "accessInfo")
        tenant = ignore_case_get(access_info, "tenant")
        vimid = ignore_case_get(vim_connections[0], "vimId")

        for resource_type in ['vdus', 'vls', 'cps', 'volume_storages']:
            for resource in ignore_case_get(self.vnfd_info, resource_type):
                if "location_info" not in resource["properties"]:
                    resource["properties"]["location_info"] = {}
                resource["properties"]["location_info"]["vimid"] = vimid
                resource["properties"]["location_info"]["tenant"] = tenant

    def do_notify_create_vim_res(self, res_type, ret):
        logger.debug('Scaling out [%s] resource' % res_type)
        resource_save_method = getattr(common, res_type + '_save')
        resource_save_method(self.job_id, self.nf_inst_id, ret)
        self.scale_out_resource[res_type].append(self.gen_del_resource(ret))

    def do_notify_del_vim_res(self, res_type, res_id):
        logger.debug('Scaling in [%s] resource, resourceid [%s]', res_type, res_id)
        resource_type = list(RESOURCE_MAP.keys())[list(RESOURCE_MAP.values()).index(res_type)]
        resource_table = globals().get(resource_type + 'InstModel')
        resource_table.objects.filter(instid=self.nf_inst_id, resourceid=res_id).delete()
        if res_type == "vm":
            VNFCInstModel.objects.filter(instid=self.nf_inst_id, vmid=res_id).delete()

    def get_scale_in_resource(self, affected_vnfcs):
        scale_in_resource = {
            'volumn': [],
            'network': [],
            'subnet': [],
            'port': [],
            'flavor': [],
            'vm': []
        }
        scale_in_vms = VmInstModel.objects.filter(instid=self.nf_inst_id)
        vms_count = scale_in_vms.count()
        for index in range(self.scale_inst_num):
            vm_index = vms_count - index - 1
            scale_in_resource["vm"].append(self.gen_del_resource(scale_in_vms[vm_index]))
            self.set_affected_vnfcs(affected_vnfcs, scale_in_vms[vm_index].resourceid)
        return scale_in_resource

    def gen_del_resource(self, res):
        is_dict = isinstance(res, dict)
        return {
            "vim_id": res["vimId"] if is_dict else res.vimid,
            "tenant_id": res["tenantId"] if is_dict else res.tenant,
            "res_id": res["id"] if is_dict else res.resourceid,
            "is_predefined": res["returnCode"] if is_dict else res.is_predefined
        }

    def get_scale_step_delta(self):
        for policy in self.vnfd_info.get("policies", []):
            if policy.get("type") != "tosca.policies.nfv.ScalingAspects":
                continue
            aspects = policy["properties"]["aspects"]
            if self.aspect_id in aspects:
                return aspects.get(self.aspect_id).get("step_deltas")[0]
        raise NFLCMException("Aspect(%s) does not exist" % self.aspect_id)

    def get_vdu_scale_aspect_deltas(self):
        for policy in self.vnfd_info.get("policies", []):
            if policy.get("type") != "tosca.policies.nfv.VduScalingAspectDeltas":
                continue
            target = policy.get("targets")[0]
            deltas = policy["properties"]["deltas"]
            if self.step_delta in deltas:
                num = int(deltas.get(self.step_delta).get("number_of_instances"))
                return target, num
        raise NFLCMException("Aspect step delta(%s) does not exist" % self.step_delta)

    def get_instance_range(self):
        for vdu in self.vnfd_info["vdus"]:
            if vdu["vdu_id"] == self.target_vdu:
                vdu_profile = vdu["properties"]["vdu_profile"]
                min_inst_num = int(vdu_profile["min_number_of_instances"])
                max_inst_num = int(vdu_profile["max_number_of_instances"])
                return min_inst_num, max_inst_num
        raise NFLCMException("VDU(%s) does not exist" % self.target_vdu)

    def check_if_can_scale(self):
        cur_inst_num = VNFCInstModel.objects.filter(instid=self.nf_inst_id).count()
        if self.is_scale_in:
            if cur_inst_num - self.scale_inst_num < self.min_instance_num:
                msg = "VNF(%s) cannot be scaled: less than min instance."
                raise NFLCMException(msg % self.nf_inst_id)
        else:
            if cur_inst_num + self.scale_inst_num > self.max_instance_num:
                msg = "VNF(%s) cannot be scaled: max instance exceeded."
                raise NFLCMException(msg % self.nf_inst_id)

    def set_affected_vnfcs(self, affected_vnfcs, vm_id):
        chgtype = CHANGE_TYPE.REMOVED if self.is_scale_in else CHANGE_TYPE.ADDED
        vnfcs = VNFCInstModel.objects.filter(instid=self.nf_inst_id, vmid=vm_id)
        vm = VmInstModel.objects.filter(instid=self.nf_inst_id, resourceid=vm_id)
        vm_resource = {}
        if vm:
            vm_resource = {
                'vimConnectionId': vm[0].vimid,
                'resourceId': vm[0].resourceid,
                'vimLevelResourceType': 'vm'
            }
        if vnfcs:
            affected_vnfcs.append({
                'id': vnfcs[0].vnfcinstanceid,
                'vduId': vnfcs[0].vduid,
                'changeType': chgtype,
                'computeResource': vm_resource
            })

    def vnf_scale_failed_handle(self, error_msg):
        logger.error('VNF scaling failed, detail message: %s', error_msg)
        self.vnf_insts.update(  # status=VNF_STATUS.FAILED,
            lastuptime=now_time())
        self.lcm_op_occ.notify_lcm(OPERATION_STATE_TYPE.FAILED, error_msg)
        JobUtil.add_job_status(self.job_id, 255, error_msg)
