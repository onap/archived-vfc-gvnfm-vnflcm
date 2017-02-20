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

from lcm.pub.utils.jobutil import enum

VNF_STATUS = enum(NULL='null', INSTANTIATING="instantiating", INACTIVE='inactive', ACTIVE="active",
                  FAILED="failed", TERMINATING="terminating", SCALING="scaling", OPERATING="operating",
                  UPDATING="updating", HEALING="healing")

vnfd_model_dict = {
    'local_storages': [],
    'vdus': [
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'2'},
            'local_storages': [],
            'vdu_id': u'vdu_omm.001',
            'image_file': u'opencos_sss_omm_img_release_20150723-1-disk1',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'omm.001',
                'manual_scale_select_vim': False},
            'description': u'singleommvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'4'},
            'local_storages': [],
            'vdu_id': u'vdu_1',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'1',
                'manual_scale_select_vim': False},
            'description': u'ompvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_2',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'2',
                'manual_scale_select_vim': False},
            'description': u'ompvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_3',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'3',
                'manual_scale_select_vim': False},
            'description': u'ompvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'4'},
            'local_storages': [],
            'vdu_id': u'vdu_10',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'10',
                'manual_scale_select_vim': False},
            'description': u'ppvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_11',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'11',
                'manual_scale_select_vim': False},
            'description': u'ppvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_12',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'12',
                'manual_scale_select_vim': False},
            'description': u'ppvm'}],
    'volumn_storages': [],
    'policies': {
        'scaling': {
            'targets': {},
            'policy_id': u'policy_scale_sss-vnf-template',
            'properties': {
                'policy_file': '*-vnfd.zip/*-vnf-policy.xml'},
            'description': ''}},
    'image_files': [
        {
            'description': '',
            'properties': {
                'name': u'opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'checksum': '',
                'disk_format': u'VMDK',
                'file_url': u'./zte-cn-sss-main-image/OMM/opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'},
            'image_file_id': u'opencos_sss_omm_img_release_20150723-1-disk1'},
        {
            'description': '',
            'properties': {
                'name': u'sss.vmdk',
                'checksum': '',
                'disk_format': u'VMDK',
                'file_url': u'./zte-cn-sss-main-image/NE/sss.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'},
            'image_file_id': u'sss'}],
    'vls': [],
    'cps': [],
    'metadata': {
        'vendor': u'zte',
        'is_shared': False,
        'description': '',
        'domain_type': u'CN',
        'version': u'v4.14.10',
        'vmnumber_overquota_alarm': False,
        'cross_dc': False,
        'vnf_type': u'SSS',
        'vnfd_version': u'V00000001',
        'id': u'sss-vnf-template',
        'name': u'sss-vnf-template'},
    "flavourId": "flavour_1",
    "instantiationLevelId": "instantiationLevel_1",
    "extVirtualLinks": [
        {
            "vlInstanceId": "1",
            "vim": {
                "vimInfoId": "1",
                "vimId": "1",
                "interfaceInfo": {
                    "vimType": "vim",
                    "apiVersion": "v2",
                    "protocolType": "http"
                },
                "accessInfo": {
                    "tenant": "tenant_vCPE",
                    "username": "vCPE",
                    "password": "vCPE_321"
                },
                "interfaceEndpoint": "http://10.43.21.105:80/"
            },
            "resourceId": "1246",
            "extCps": [
                {
                    "cpdId": "11",
                    "addresses": [
                        {
                            "addressType": "MAC",
                            "l2AddressData": "00:f3:43:20:a2:a3"
                        },
                        {
                            "addressType": "IP",
                            "l3AddressData": {
                                "iPAddressType": "IPv4",
                                "iPAddress": "192.168.104.2"
                            }
                        }
                    ],
                    "numDynamicAddresses": 0
                }
            ]
        }
    ],
    "localizationLanguage": "en_US",
    "additionalParams": {}
}