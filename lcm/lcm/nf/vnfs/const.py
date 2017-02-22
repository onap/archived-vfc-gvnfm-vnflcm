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
        'name': u'sss-vnf-template'
    },
    'vdus': [
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'2'
            },
            'local_storages': [

            ],
            'vdu_id': u'vdu_omm.001',
            'image_file': u'opencos_sss_omm_img_release_20150723-1-disk1',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
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
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': u'omm.001',
                'manual_scale_select_vim': False
            },
            'description': u'singleommvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'
            },
            'local_storages': [

            ],
            'vdu_id': u'vdu_12',
            'image_file': u'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
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
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': u'12',
                'manual_scale_select_vim': False
            },
            'description': u'ppvm'
        }
    ],
    'volume_storages': [
        {
            "volume_storage_id": "volume_storage1",
            "description": "",
            "properties": {
                "size": "100 GB",
                "volume_id": "",
                "volume_name": "volumeStorage1",
                "custom_volume_type": "type1",
                "disk_type": "data",
                "delete_on_termination_vm": True,
                "location_info": {
                    "vimid": "vimid_1",
                    "tenant": "tenantname_1",
                    "availability_zone": "zone1"
                },
                "is_predefined": False,
                "is_shared": False
            },
            "image_file": [
                "volume_image"
            ]
        }
    ],
    'policies': {
        'scaling': {
            'targets': {

            },
            'policy_id': u'policy_scale_sss-vnf-template',
            'properties': {
                'policy_file': '*-vnfd.zip/*-vnf-policy.xml'
            },
            'description': ''
        }
    },
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
                'hypervisor_type': 'kvm'
            },
            'image_file_id': u'opencos_sss_omm_img_release_20150723-1-disk1'
        },
        {
            'description': '',
            'properties': {
                'name': u'sss.vmdk',
                'checksum': '',
                'disk_format': u'VMDK',
                'file_url': u'./zte-cn-sss-main-image/NE/sss.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'
            },
            'image_file_id': u'sss'
        }
    ],
    'vls': [
        {
            "vl_id": "vldId1",
            "description": "",
            "properties": {
                "name": "umac_241_control",
                "network_name": "umac_control",
                "is_predefined": False,
                "vendor": "zte",
                "netmask": "255.255.255.0",
                "mtu": 1500,
                "network_type": "vlan",
                "physical_network": "phynet01",
                "segmentation_id": "30",
                "vlan_transparent": False,
                "vds_name": "vds1",
                "cidr": "192.168.199.0/24",
                "ip_version": 4,
                "gateway_ip": "192.168.199.1",
                "dhcp_enabled": False,
                "dns_nameservers": [
                    "192.168.0.4",
                    "192.168.0.10"
                ],
                "start_ip": "192.168.199.2",
                "end_ip": "192.168.199.254",
                "host_routes": [
                    {
                        "destination": "10.43.26.0/24",
                        "nexthop": "10.41.23.1"
                    }
                ],
                "location_info": {
                    "vimid": "vimid_1",
                    "tenant": "tenantname_1"
                },
                "cloud_type": "IaaS"
            },
            "route_id": "router01",
            "route_external": False
        }
    ],
    'cps': [
        {
            "cp_id": "cpId",
            "description": "",
            "properties": {
                "name": "",
                "mac_address": "00:d9:00:82:11:e1",
                "ip_address:": "192.168.1.21",
                "ip_range_start": "192.168.1.20",
                "ip_range_end": "192.168.1.29",
                "floating_ip_address": {
                    "external_network": "extnet01",
                    "ip_address": "10.43.53.23"
                },
                "service_ip_address": "192.168.1.23",
                "order": 1,
                "bandwidth": 1000,
                "vnic_type": "normal",
                "allowed_address_pairs": [
                    {
                        "ip": "192.168.1.13",
                        "mac": "00:f3:43:20:a2:a3"
                    }
                ],
                "bond": "none",
                "bond_index": 1,
                "macbond": "00:d9:00:82:11:d1",
                "sfc_encapsulation": "",
                "direction": "",
                "gateway_ip": "192.168.199.1",
                "netmask": "255.255.255.0",
                "interface_name": "fe-01-02",
                "is_virtual": False,
                "function": "control"
            },
            "vl_id": "vldId1",
            "vdu_id": u'vdu_omm.001'
        }
    ],
    'local_storages': [

    ],
}

c1_data_get_tenant_id = {  # get_tenant_id
    "tenants": [
        {
            "id": "1",
            "name": "tenantname_1"
        }
    ]
}
c2_data_create_volume = {
    "id": "4bd3e9eb-cd8b-456a-8589-910836a0ab31",
    "name": "volume1",
    "returnCode": 1,
    "vimId": "vim_volume_1",
    "vimName": "vim_volume_1",
    "tenantId": "vim_volume_1",
    "volumeType": "123",
    "availabilityZone": "availabilityZone",
    "status": "availuable",
    "createTime": "2015-12-02T06:39:40.000000",
    "type": None,
    "size": 40
}
c3_data_get_volume = {  # get_volume
    "status": "available",
    "name": "wangsong",
    "attachments": [
        {
            "device": "/dev/vdc",
            "serverId": "3030e666-528e-4954-88f5-cc21dab1262b",
            "volumeId": "4bd3e9eb-cd8b-456a-8589-910836a0ab31",
            "hostName": None,
            "id": "4bd3e9eb-cd8b-456a-8589-910836a0ab31"
        }
    ],
    "createTime": "2015-12-02T06:39:40.000000",
    "type": None,
    "id": "4bd3e9eb-cd8b-456a-8589-910836a0ab31",
    "size": 40
}
c4_data_create_network = {  # create_network
    "returnCode": 0,
    "vimId": "11111",
    "vimName": "11111",
    "status": "ACTIVE",
    "id": "3c9eebdbbfd345658269340b9ea6fb73",
    "name": "net1",
    "tenantId": "tenant1",
    "networkName": "ommnet",
    "shared": True,
    "vlanTransparent": True,
    "networkType": "vlan",
    "segmentationId": 202,
    "physicalNetwork": "ctrl",
    "routerExternal": False
}
c5_data_create_subnet = {
    "returnCode": 0,
    "vimId": "11111",
    "vimName": "11111",
    "status": " ACTIVE",
    "id": "d62019d3-bc6e-4319-9c1d-6722fc136a23",
    "tenantId": "tenant1",
    "networkId": "d32019d3-bc6e-4319-9c1d-6722fc136a22",
    "networkName": "networkName",
    "name": "subnet1",
    "cidr": "10.43.35.0/24",
    "ipVersion": 4,
    "enableDhcp": 1,
    "gatewayIp": "10.43.35.1",
    "dnsNameservers": [],
    "allocationPools": [
        {
            "start": "192.168.199.2",
            "end": "192.168.199.254"
        }
    ],
    "hostRoutes": []
}
c6_data_create_port = {
    "returnCode": 0,
    "vimId": "11111",
    "vimName": "11111",
    "status": " ACTIVE",
    "id": " 872019d3-bc6e-4319-9c1d-6722fc136afg",
    "tenantId": "tenant1",
    "name": "subnet1",
    "networkId": "d32019d3-bc6e-4319-9c1d-6722fc136a22",
    "networkName": "networkName",
    "subnetId": "d62019d3-bc6e-4319-9c1d-6722fc136a23",
    "subnetName": "subnet1",
    "macAddress": "212.12.61.23",
    "ip": "10.43.38.11",
    "vnicType": "normal",
    "securityGroups": ""
}