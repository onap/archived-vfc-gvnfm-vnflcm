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

from lcm.pub.utils.jobutil import enum

HEAL_ACTION_TYPE = enum(START="vmCreate", RESTART="vmReset")
ACTION_TYPE = enum(START=1, STOP=2, REBOOT=3)
GRANT_TYPE = enum(INSTANTIATE="Instantiate", TERMINATE="Terminate", HEAL_CREATE="Heal Create", HEAL_RESTART="Heal Restart", OPERATE="Operate")
VNF_STATUS = enum(NULL='null', INSTANTIATING="instantiating", INACTIVE='inactive', ACTIVE="active",
                  FAILED="failed", TERMINATING="terminating", SCALING="scaling", OPERATING="operating",
                  UPDATING="updating", HEALING="healing")

RESOURCE_MAP = {'Storage': 'volumn', 'Network': 'network', 'SubNetwork': 'subnet', 'Port': 'port',
                'Flavour': 'flavor', 'Vm': 'vm'}

ROOT_URI = "api/vnflcm/v1/subscriptions/"

AUTH_TYPES = ["BASIC", "OAUTH2_CLIENT_CREDENTIALS", "TLS_CERT"]

BASIC = "BASIC"

OAUTH2_CLIENT_CREDENTIALS = "OAUTH2_CLIENT_CREDENTIALS"

LCCNNOTIFICATION = "VnfLcmOperationOccurrenceNotification"

NOTIFICATION_TYPES = [
    "VnfLcmOperationOccurrenceNotification",
    "VnfIdentifierCreationNotification",
    "VnfIdentifierDeletionNotification"
]

LCM_OPERATION_TYPES = [
    "INSTANTIATE",
    "SCALE",
    "SCALE_TO_LEVEL",
    "CHANGE_FLAVOUR",
    "TERMINATE",
    "HEAL",
    "OPERATE",
    "CHANGE_EXT_CONN",
    "MODIFY_INFO"
]

LCM_OPERATION_STATE_TYPES = [
    "STARTING",
    "PROCESSING",
    "COMPLETED",
    "FAILED_TEMP",
    "FAILED",
    "ROLLING_BACK",
    "ROLLED_BACK"
]


inst_req_data = {
    "flavourId": "flavour_1",
    "instantiationLevelId": "instantiationLevel_1",
    "extVirtualLinks": [
        {
            "id": "extVirtualLink_1",
            "vimConnectionId": "vimConnection_1",
            "resourceProviderId": "resourceProvider_1",
            "resourceId": "resource_1",
            "resourceSubnetId": "resourceSubnet_1",
            "extCps": [
                {
                    "cpdId": "cpd_1",
                    "cpConfig": [
                        {
                            "cpInstanceId": "cpInstance_1",
                            "linkPortId": "linkPort_1",
                            "cpProtocolData": [
                                {
                                    "layerProtocol": "IP_OVER_ETHERNET",
                                    "ipOverEthernet": {
                                        "macAddress": "00:f3:43:20:a2:a3",
                                        "ipAddresses": [
                                            {
                                                "type": "IPV4",
                                                "fixedAddresses": ["192.168.104.2", ],
                                                "numDynamicAddresses": 0,
                                                "addressRange": None,
                                                "subnetId": "subnet_1",
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            ],
            "extLinkPorts": [
                {
                    "id": "extLinkPort_1",
                    "resourceHandle": {
                        "vimConnectionId": "vimConnection_1",
                        "resourceProviderId": "resourceProvider_1",
                        "resourceId": "resource_1",
                        "vimLevelResourceType": "vimLevelResourceType_1",
                    }
                }
            ]
        }
    ],
    "extManagedVirtualLinks": [
        {
            "id": 'extManagedVirtualLink_1',
            "virtualLinkDescId": 'virtualLinkDesc_1',
            "vimConnectionId": 'vimConnection_1',
            "resourceProviderId": 'resourceProvider_1',
            "resourceId": 'resource_1',
        }
    ],
    "vimConnectionInfo": [
        {
            "id": 'vimConnection_1',
            "vimId": 'vim_1',
            "vimType": 'vim',
            "interfaceInfo": {
                "apiVersion": "apiVersion_1",
                "protocolType": "http"
            },
            "accessInfo": {
                "tenant": "tenant_vCPE",
                "username": "vCPE",
                "password": "vCPE_321",
            },
            "extra": None,
        }
    ],
    "localizationLanguage": "en_US",
    "additionalParams": {
        "vimId": "vim_1",
        "key1": "test1",
        "key2": "test2",
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
            "vdu_id": "vdu1Id",
            "description": "vdu description",
            "properties": {
                "name": "vduinstname",
                "vdu_type": "OMP",
                "key_vdu": True,
                "support_scaling": True,
                "location_info": {
                    "vimid": "vimid",
                    "tenant": "tenantname",
                    "availability_zone": "zone1",
                    "host": "host1"
                },
                "local_affinity_antiaffinity_rule": [
                    {
                        "affinity_antiaffinity": "anti-affinity",
                        "scope": "node"
                    },
                    {
                        "affinity_antiaffinity": "affinity",
                        "scope": "zone"
                    }
                ],
                "inject_data_list": [
                    {
                        "file_name": "abc.xml",
                        "file_data": "<a>xxx</a><b>ssss</b>"
                    }
                ],
                "storage_policy": "HIGH",
                "template_id": "26",
                "manual_scale_select_vim": False,
                "watchdog": {
                    "enabledelay": 600000,
                    "action": "reset"
                },
                "is_predefined": False,
                "allow_scale_updown": False,
                "inject_network_address": True,
                "inner_hugepage_num": 100,
                "inner_hugepage_size": "2048",
                "action": "add"
            },
            "image_file": u'sss',
            "local_storages": [
                "local_storage_id1",
                "local_storage_id2"
            ],
            "volume_storages": [
                {
                    "volume_storage_id": "volume_storage1",
                    "location": "/usr/data",
                    "device": "/dev/hda1"
                }
            ],
            "dependencies": [
                "vdu1Id",
                "vduNId"
            ],
            "nfv_compute": {
                "num_cpus": 4,
                "mem_size": "1 GB",
                "cpu_frequency": "1GHz",
                "flavor_extra_specs": {
                    "hw: cpu_policy": "shared",
                    "hw: cpu_max_threads": 50,
                    "hw: cpu_sockets": 10,
                    "hw: cpu_max_sockets": 20,
                    "hw: cpu_max_cores": 8,
                    "hw: cpu_threads": 30,
                    "hw: numa_mem.0": 12288,
                    "hw: hugepage_num": 100,
                    "hw: high_performance": "dvs_high",
                    "hw: numa_nodes": 1,
                    "hw: numa_cpus.0": "2,4,8",
                    "hw: numa_pci": True,
                    "hw: cpu_cores": 4,
                    "pci_passthrough: alias": "ColetoCreek: 1",
                    "hw: mem_page_size": "large",
                    "hw: mem_paging_mechanism": "EPT"
                }
            },
            "vls": [
                "vlId1",
            ],
            "cps": [
                "cpId1",
            ],
            "scalable": {
                "min_instances": 1,
                "max_instances": 2,
                "default_instances": 1
            },
            "interfaces": {
                "Standard": {
                    "create": {
                        "implementation": "<implementationScript>",
                        "inputs": {
                            "param1Name": "value1",
                            "paramNName": "valueN"
                        }
                    },
                    "configure": {
                        "implementation": "<implementationScript>",
                        "inputs": {
                            "param1Name": "value1",
                            "paramNName": "valueN"
                        }
                    },
                    "start": {
                        "implementation": "<implementationScript>",
                        "inputs": {
                            "param1Name": "value1",
                            "paramNName": "valueN"
                        }
                    },
                    "stop": {
                        "implementation": "<implementationScript>",
                        "inputs": {
                            "param1Name": "value1",
                            "paramNName": "valueN"
                        }
                    },
                    "delete": {
                        "implementation": "<implementationScript>",
                        "inputs": {
                            "param1Name": "value1",
                            "paramNName": "valueN"
                        }
                    }
                }
            },
            "artifacts": [
                {
                    "artifact_name": "software_version_file",
                    "type": "tosca.artifacts.Deployment",
                    "file": "AppSoftwares/zte-cn-xgw-V5.16.11_NFV-version.zip",
                    "repository": "",
                    "deploy_path": ""
                }
            ]
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
            "cp_id": "cpId1",
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
            "vdu_id": "vdu1Id"
        }
    ],
    'local_storages': [

    ],
}

# get_tenant_id
c1_data_get_tenant_id = {
    "tenants": [
        {
            "id": "1",
            "name": "chinamobile"
        }
    ]
}

# create_volume
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

# get_volume
c3_data_get_volume = {
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

# create_network
c4_data_create_network = {
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
    "physicalNetwork": "physnet1",
    "routerExternal": False
}

# create_subnet
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

# create_ports
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
    "vnicType": "direct",
    "securityGroups": ""
}

# create_flavor
c7_data_create_flavor = {
    "returnCode": 0,
    "vimId": "11111",
    "vimName": "11111",
    "id": "142019d3-bc6e-4319-9c1d-6722fc136afg",
    "tenantId": "tenant1",
    "name": "subnet1",
    "vcpu": 5,
    "memory": 2,
    "disk": 40,
    "ephemeral": 40,
    "swap": 20,
    "isPublic": True,
    "extraSpecs": "testtt"
}

# list_image
c8_data_list_image = {
    "vimid": "",
    "vimname": "",
    "images": [
        {
            "status": "active",
            "id": "5e2757c1-f846-4727-915c-9a872553ed75",
            "size": 862016,
            "name": u'sss.vmdk'
        }
    ]
}

# create_vm
c9_data_create_vm = {
    "returnCode": 1,
    "id": "3c9eebdbbfd345658269340b9ea6fb73",
    "name": "vm1",
    "vimId": "11111",
    "vimName": "11111",
    "tenantId": "tenant1",
    "boot": "boot_1",
    "nicArray": "dfdf",
    "volumeArray": "dfdf",
    "availabilityZone": "fdvfdv",
    "flavorId": "fdvfdv",
    "metadata": "fdvfdv",
    "securityGroups": "fdvfdv",
    "serverGroup": "fdvfdv",
    "status": "ACTIVE"
}

# get_vm
c10_data_get_vm = {
    "returnCode": 1,
    "id": "3c9eebdbbfd345658269340b9ea6fb73",
    "name": "vm1",
    "vimId": "11111",
    "vimName": "11111",
    "tenantId": "tenant1",
    "status": "ACTIVE"
}

vnfdModel = {
    "volume_storages": [
        {
            "volume_storage_id": "test",
            "properties": {
                "location_info": {
                    "vimid": "vim_1",
                    "tenant": "chinamobile",
                    "availability_zone": "test",
                },
                "volume_name": "test",
                "custom_volume_type": "test",
                "size": "10 GB",
            },
            "image_file": "test",
        },
    ],
    "vls": [
        {
            "vl_id": "test",
            "properties": {
                "location_info": {
                    "vimid": "test",
                    "tenant": "chinamobile",
                },
                "vl_profile": {
                    "networkName": "test",
                    "networkType": "test",
                    "physicalNetwork": "test",
                    "vlanTransparent": "test",
                    "segmentationId": "1",
                    "cidr": "test",
                    "dhcpEnabled": "test",
                    "gatewayIp": "test",
                    "startIp": "test",
                    "endIp": "test",
                },
                "connectivity_type": {
                    "layer_protocol": "ipv4",
                },
                "dns_nameservers": "test",
                "host_routes": "test",
            },
            "route_external": "test",
        }
    ],
    "cps": [
        {
            "vdu_id": "test",
            "cp_id": "cp1",
            "networkId": "",  # TODO
            "subnetId": "",  # TODO
            "vl_id": "test",
            "properties": {
                "name": "test",
                "mac_address": "test",
                "protocol_data": [
                    {
                        "address_data": {
                            "l3_address_data": {
                                "fixed_ip_address": "test"
                            },
                        },
                    },
                ],
                "vnic_type": "direct",
                "role": "root",
                "virtual_network_interface_requirements": [
                    {
                        "network_interface_requirements": {
                            "interfaceType": '{"schema-version": "0", "schema-location":"", "platform-id": "generic", "mandatory": false, "configuration-value": "SR-IOV"}'
                        },
                        "support_mandatory": False,
                        "name": "SRIOV_Port",
                        "description": "sriov"
                    }
                ]
            }
        }
    ],
    "vdus": [
        {
            "vdu_id": "test",
            "properties": {
                "location_info": {
                    "vimid": "test",
                    "tenant": "chinamobile",
                    "availability_zone": "test",
                },
                "name": "test",
                "inject_files": [],
                "user_data": "test",
                "meta_data": {},
            },
            "cps": [],
            "type": "tosca.nodes.nfv.Vdu.Compute",
            "virtual_compute": {
                "virtual_cpu": {
                    "num_virtual_cpu": "16",
                },
                "virtual_memory": {
                    "virtual_mem_size": "8000 MB",
                    "vdu_memory_requirements": {
                        "memoryPageSize": "8 MB",
                    },
                },
            },
            "virtual_storage": {
                "type_of_storage": "ephemeral",
                "size_of_storage": "10 GB",
            },
            "type": "tosca.nodes.nfv.Vdu.Compute",
            "artifacts": [
                {
                    "artifact_name": "sw_image",
                    "file": "sss.vmdk",
                },
            ],
            "volume_storages": [
                {
                    "volume_storage_id": "test",
                }
            ],
        },
    ],
    "image_files": [],
    "routers": [],
    "local_storages": [],
    "vnf_exposed": {
        "external_cps": [],
        "forward_cps": []
    },
    "inputs": {
        "pe1_id": {
            "type": "string",
            "description": "pe1_idofunderlayvpn"
        },
        "pe2_id": {
            "type": "string",
            "description": "pe2_idofunderlayvpn"
        },
        "serviceType": {
            "type": "string",
            "description": "serviceTypeofunderlayvpn"
        },
        "description": {
            "type": "string",
            "description": "descriptionofunderlayvpn"
        },
        "ac2_route": {
            "type": "string",
            "description": "ac2_routeofunderlayvpn"
        },
        "ac1_route": {
            "type": "string",
            "description": "ac1_routeofunderlayvpn"
        },
        "ac1_svlan": {
            "type": "integer",
            "description": "ac1_svlanofunderlayvpn"
        },
        "ac2_ip": {
            "type": "string",
            "description": "ac2_ipofunderlayvpn"
        },
        "ac1_ip": {
            "type": "string",
            "description": "ac1_ipofunderlayvpn"
        },
        "ac2_port": {
            "type": "string",
            "description": "ac2_portofunderlayvpn"
        },
        "topology": {
            "type": "string",
            "description": "topologyofunderlayvpn"
        },
        "technology": {
            "type": "string",
            "description": "technologyofunderlayvpn"
        },
        "ac1_port": {
            "type": "string",
            "description": "ac1_portofunderlayvpn"
        },
        "ac2_svlan": {
            "type": "integer",
            "description": "ac2_svlanofunderlayvpn"
        },
        "name": {
            "type": "string",
            "description": "Nameofunderlayervpn"
        }
    },
    "metadata": {
        "designer": "sdno",
        "name": "underlayervpn",
        "csarVersion": "1.0",
        "csarType": "SSAR",
        "csarProvider": "huawei",
        "version": "1.0",
        "type": "SSAR",
        "id": "ns_underlayervpn_1_0"
    }
}

vnfpackage_info = {
    "imageInfo": [],
    "csarId": "vOpenNAT",
    "packageInfo": {
        "csarName": "vOpenNAT.csar",
        "vnfdModel": json.dumps(vnfdModel),
        "vnfdProvider": "Intel",
        "vnfdId": "openNAT_1.0",
        "downloadUrl": "http://10.96.33.39:8806/static/catalog/vOpenNAT/vOpenNAT.csar",
        "vnfVersion": "v1.0",
        "vnfdVersion": "v1.0",
        "vnfPackageId": "vOpenNAT"
    }
}

# # vnfd_rawdata
# vnfd_rawdata = {
#     "rawData": {
#         "instance": {
#             "metadata": {
#                 "designer": "sdno",
#                 "name": "underlayervpn",
#                 "csarVersion": "1.0",
#                 "csarType": "SSAR",
#                 "csarProvider": "huawei",
#                 "version": "1.0",
#                 "type": "SSAR",
#                 "id": "ns_underlayervpn_1_0"
#             },
#             "nodes": [
#                 {
#                     "id": "ac2_fdhrbk3dvan8hl5wifm9lp1e9",
#                     "type_name": "tosca.nodes.sdn.l3ac",
#                     "template_name": "ac2",
#                     "properties": {
#                         "ip": {
#                             "type_name": "string"
#                         },
#                         "route": {
#                             "type_name": "string"
#                         },
#                         "port": {
#                             "type_name": "string"
#                         },
#                         "svlan": {
#                             "type_name": "string"
#                         }
#                     },
#                     "interfaces": [
#                         {
#                             "name": "Standard",
#                             "type_name": "tosca.interfaces.node.lifecycle.Standard"
#                         }
#                     ],
#                     "capabilities": [
#                         {
#                             "name": "feature",
#                             "type_name": "tosca.capabilities.Node"
#                         },
#                         {
#                             "name": "ac",
#                             "type_name": "tosca.capabilities.sdn.ac"
#                         }
#                     ],
#                     "relationships": [
#                         {
#                             "target_node_id": "pe2_go3vo1ctxr1vlbl0ij8stbtj6",
#                             "target_capability_name": "feature"
#                         },
#                         {
#                             "target_node_id": "ac2_fdhrbk3dvan8hl5wifm9lp1e9",
#                             "target_capability_name": "feature"
#                         }
#                     ]
#                 },
#                 {
#                     "id": "ac1_jqows1ai0j0cmwk9jdvuknt97",
#                     "type_name": "tosca.nodes.sdn.l3ac",
#                     "template_name": "ac1",
#                     "properties": {
#                         "ip": {
#                             "type_name": "string"
#                         },
#                         "route": {
#                             "type_name": "string"
#                         },
#                         "port": {
#                             "type_name": "string"
#                         },
#                         "svlan": {
#                             "type_name": "string"
#                         }
#                     },
#                     "interfaces": [
#                         {
#                             "name": "Standard",
#                             "type_name": "tosca.interfaces.node.lifecycle.Standard"
#                         }
#                     ],
#                     "capabilities": [
#                         {
#                             "name": "feature",
#                             "type_name": "tosca.capabilities.Node"
#                         },
#                         {
#                             "name": "ac",
#                             "type_name": "tosca.capabilities.sdn.ac"
#                         }
#                     ],
#                     "relationships": [
#                         {
#                             "target_node_id": "pe1_e58ekps6m45g6w9egs9lue2j7",
#                             "target_capability_name": "feature"
#                         },
#                         {
#                             "target_node_id": "ac2_fdhrbk3dvan8hl5wifm9lp1e9",
#                             "target_capability_name": "feature"
#                         }
#                     ]
#                 },
#                 {
#                     "id": "vpn_ie0xim076f7cje67fvrrq9tg1",
#                     "type_name": "tosca.nodes.sdn.underlayVPN",
#                     "template_name": "vpn",
#                     "properties": {
#                         "serviceType": {
#                             "type_name": "string"
#                         },
#                         "description": {
#                             "type_name": "string"
#                         },
#                         "name": {
#                             "type_name": "string"
#                         },
#                         "topology": {
#                             "type_name": "string"
#                         }
#                     },
#                     "interfaces": [
#                         {
#                             "name": "Standard",
#                             "type_name": "tosca.interfaces.node.lifecycle.Standard"
#                         }
#                     ],
#                     "capabilities": [
#                         {
#                             "name": "feature",
#                             "type_name": "tosca.capabilities.Node"
#                         }
#                     ],
#                     "relationships": [
#                         {
#                             "target_node_id": "ac1_jqows1ai0j0cmwk9jdvuknt97",
#                             "target_capability_name": "feature"
#                         },
#                         {
#                             "target_node_id": "ac2_fdhrbk3dvan8hl5wifm9lp1e9",
#                             "target_capability_name": "feature"
#                         }
#                     ]
#                 },
#                 {
#                     "id": "pe1_e58ekps6m45g6w9egs9lue2j7",
#                     "type_name": "tosca.nodes.sdn.l3pe",
#                     "template_name": "pe1",
#                     "properties": {
#                         "id": {
#                             "type_name": "string"
#                         }
#                     },
#                     "interfaces": [
#                         {
#                             "name": "Standard",
#                             "type_name": "tosca.interfaces.node.lifecycle.Standard"
#                         }
#                     ],
#                     "capabilities": [
#                         {
#                             "name": "feature",
#                             "type_name": "tosca.capabilities.Node"
#                         },
#                         {
#                             "name": "pe",
#                             "type_name": "tosca.capabilities.sdn.pe"
#                         }
#                     ]
#                 },
#                 {
#                     "id": "pe2_go3vo1ctxr1vlbl0ij8stbtj6",
#                     "type_name": "tosca.nodes.sdn.l3pe",
#                     "template_name": "pe2",
#                     "properties": {
#                         "id": {
#                             "type_name": "string"
#                         }
#                     },
#                     "interfaces": [
#                         {
#                             "name": "Standard",
#                             "type_name": "tosca.interfaces.node.lifecycle.Standard"
#                         }
#                     ],
#                     "capabilities": [
#                         {
#                             "name": "feature",
#                             "type_name": "tosca.capabilities.Node"
#                         },
#                         {
#                             "name": "pe",
#                             "type_name": "tosca.capabilities.sdn.pe"
#                         }
#                     ]
#                 }
#             ],
#             "substitution": {
#                 "node_type_name": "tosca.nodes.sdn.ext.NS.ns_underlayervpn"
#             },
#             "inputs": {
#                 "ac2_ip": {
#                     "type_name": "string",
#                     "description": "ac2_ipofunderlayvpn"
#                 },
#                 "ac2_route": {
#                     "type_name": "string",
#                     "description": "ac2_routeofunderlayvpn"
#                 },
#                 "serviceType": {
#                     "type_name": "string",
#                     "description": "serviceTypeofunderlayvpn"
#                 },
#                 "description": {
#                     "type_name": "string",
#                     "description": "descriptionofunderlayvpn"
#                 },
#                 "pe2_id": {
#                     "type_name": "string",
#                     "description": "pe2_idofunderlayvpn"
#                 },
#                 "ac1_route": {
#                     "type_name": "string",
#                     "description": "ac1_routeofunderlayvpn"
#                 },
#                 "ac1_svlan": {
#                     "type_name": "integer",
#                     "description": "ac1_svlanofunderlayvpn"
#                 },
#                 "name": {
#                     "type_name": "string",
#                     "description": "Nameofunderlayervpn"
#                 },
#                 "ac1_ip": {
#                     "type_name": "string",
#                     "description": "ac1_ipofunderlayvpn"
#                 },
#                 "ac2_port": {
#                     "type_name": "string",
#                     "description": "ac2_portofunderlayvpn"
#                 },
#                 "pe1_id": {
#                     "type_name": "string",
#                     "description": "pe1_idofunderlayvpn"
#                 },
#                 "technology": {
#                     "type_name": "string",
#                     "description": "technologyofunderlayvpn"
#                 },
#                 "ac1_port": {
#                     "type_name": "string",
#                     "description": "ac1_portofunderlayvpn"
#                 },
#                 "ac2_svlan": {
#                     "type_name": "integer",
#                     "description": "ac2_svlanofunderlayvpn"
#                 },
#                 "topology": {
#                     "type_name": "string",
#                     "description": "topologyofunderlayvpn"
#                 }
#             }
#         }
#     }
# }
