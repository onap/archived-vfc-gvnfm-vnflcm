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

vnfd_rawdata = {
    "rawData": {
        "instance": {
            "metadata": {
                "designer": "sdno",
                "name": "underlayervpn",
                "csarVersion": "1.0",
                "csarType": "SSAR",
                "csarProvider": "huawei",
                "version": "1.0",
                "type": "SSAR",
                "id": "ns_underlayervpn_1_0"
            },
            "nodes": [
                {
                    "id": "ac2_fdhrbk3dvan8hl5wifm9lp1e9",
                    "type_name": "tosca.nodes.sdn.l3ac",
                    "template_name": "ac2",
                    "properties": {
                        "ip": {
                            "type_name": "string"
                        },
                        "route": {
                            "type_name": "string"
                        },
                        "port": {
                            "type_name": "string"
                        },
                        "svlan": {
                            "type_name": "string"
                        }
                    },
                    "interfaces": [
                        {
                            "name": "Standard",
                            "type_name": "tosca.interfaces.node.lifecycle.Standard"
                        }
                    ],
                    "capabilities": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        },
                        {
                            "name": "ac",
                            "type_name": "tosca.capabilities.sdn.ac"
                        }
                    ],
                    "relationships": [
                        {
                            "target_node_id": "pe2_go3vo1ctxr1vlbl0ij8stbtj6",
                            "target_capability_name": "feature"
                        },
                        {
                            "target_node_id": "ac2_fdhrbk3dvan8hl5wifm9lp1e9",
                            "target_capability_name": "feature"
                        }
                    ]
                },
                {
                    "id": "ac1_jqows1ai0j0cmwk9jdvuknt97",
                    "type_name": "tosca.nodes.sdn.l3ac",
                    "template_name": "ac1",
                    "properties": {
                        "ip": {
                            "type_name": "string"
                        },
                        "route": {
                            "type_name": "string"
                        },
                        "port": {
                            "type_name": "string"
                        },
                        "svlan": {
                            "type_name": "string"
                        }
                    },
                    "interfaces": [
                        {
                            "name": "Standard",
                            "type_name": "tosca.interfaces.node.lifecycle.Standard"
                        }
                    ],
                    "capabilities": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        },
                        {
                            "name": "ac",
                            "type_name": "tosca.capabilities.sdn.ac"
                        }
                    ],
                    "relationships": [
                        {
                            "target_node_id": "pe1_e58ekps6m45g6w9egs9lue2j7",
                            "target_capability_name": "feature"
                        },
                        {
                            "target_node_id": "ac2_fdhrbk3dvan8hl5wifm9lp1e9",
                            "target_capability_name": "feature"
                        }
                    ]
                },
                {
                    "id": "vpn_ie0xim076f7cje67fvrrq9tg1",
                    "type_name": "tosca.nodes.sdn.underlayVPN",
                    "template_name": "vpn",
                    "properties": {
                        "serviceType": {
                            "type_name": "string"
                        },
                        "description": {
                            "type_name": "string"
                        },
                        "name": {
                            "type_name": "string"
                        },
                        "topology": {
                            "type_name": "string"
                        }
                    },
                    "interfaces": [
                        {
                            "name": "Standard",
                            "type_name": "tosca.interfaces.node.lifecycle.Standard"
                        }
                    ],
                    "capabilities": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        }
                    ],
                    "relationships": [
                        {
                            "target_node_id": "ac1_jqows1ai0j0cmwk9jdvuknt97",
                            "target_capability_name": "feature"
                        },
                        {
                            "target_node_id": "ac2_fdhrbk3dvan8hl5wifm9lp1e9",
                            "target_capability_name": "feature"
                        }
                    ]
                },
                {
                    "id": "pe1_e58ekps6m45g6w9egs9lue2j7",
                    "type_name": "tosca.nodes.sdn.l3pe",
                    "template_name": "pe1",
                    "properties": {
                        "id": {
                            "type_name": "string"
                        }
                    },
                    "interfaces": [
                        {
                            "name": "Standard",
                            "type_name": "tosca.interfaces.node.lifecycle.Standard"
                        }
                    ],
                    "capabilities": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        },
                        {
                            "name": "pe",
                            "type_name": "tosca.capabilities.sdn.pe"
                        }
                    ]
                },
                {
                    "id": "pe2_go3vo1ctxr1vlbl0ij8stbtj6",
                    "type_name": "tosca.nodes.sdn.l3pe",
                    "template_name": "pe2",
                    "properties": {
                        "id": {
                            "type_name": "string"
                        }
                    },
                    "interfaces": [
                        {
                            "name": "Standard",
                            "type_name": "tosca.interfaces.node.lifecycle.Standard"
                        }
                    ],
                    "capabilities": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        },
                        {
                            "name": "pe",
                            "type_name": "tosca.capabilities.sdn.pe"
                        }
                    ]
                }
            ],
            "substitution": {
                "node_type_name": "tosca.nodes.sdn.ext.NS.ns_underlayervpn"
            },
            "inputs": {
                "ac2_ip": {
                    "type_name": "string",
                    "description": "ac2_ipofunderlayvpn"
                },
                "ac2_route": {
                    "type_name": "string",
                    "description": "ac2_routeofunderlayvpn"
                },
                "serviceType": {
                    "type_name": "string",
                    "description": "serviceTypeofunderlayvpn"
                },
                "description": {
                    "type_name": "string",
                    "description": "descriptionofunderlayvpn"
                },
                "pe2_id": {
                    "type_name": "string",
                    "description": "pe2_idofunderlayvpn"
                },
                "ac1_route": {
                    "type_name": "string",
                    "description": "ac1_routeofunderlayvpn"
                },
                "ac1_svlan": {
                    "type_name": "integer",
                    "description": "ac1_svlanofunderlayvpn"
                },
                "name": {
                    "type_name": "string",
                    "description": "Nameofunderlayervpn"
                },
                "ac1_ip": {
                    "type_name": "string",
                    "description": "ac1_ipofunderlayvpn"
                },
                "ac2_port": {
                    "type_name": "string",
                    "description": "ac2_portofunderlayvpn"
                },
                "pe1_id": {
                    "type_name": "string",
                    "description": "pe1_idofunderlayvpn"
                },
                "technology": {
                    "type_name": "string",
                    "description": "technologyofunderlayvpn"
                },
                "ac1_port": {
                    "type_name": "string",
                    "description": "ac1_portofunderlayvpn"
                },
                "ac2_svlan": {
                    "type_name": "integer",
                    "description": "ac2_svlanofunderlayvpn"
                },
                "topology": {
                    "type_name": "string",
                    "description": "topologyofunderlayvpn"
                }
            }
        }
    }
}


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