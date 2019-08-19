# Copyright (C) 2019 ZTE. All Rights Reserved.
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


vnfd_model1 = {
    'metadata': {
        'vendor': 'zte',
        'is_shared': False,
        'description': '',
        'domain_type': 'CN',
        'version': 'v4.14.10',
        'vmnumber_overquota_alarm': False,
        'cross_dc': False,
        'vnf_type': 'SSS',
        'vnfd_version': 'V00000001',
        'id': 'sss-vnf-template',
        'name': 'sss-vnf-template'
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
            "image_file": 'sss',
            "local_storages": [
                "local_storage_id1",
                "local_storage_id2"
            ],
            "virtual_storages": [
                {
                    "virtual_storage_id": "volume_storage1",
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
            ]
        }
    ],
    'volume_storages': [
        {
            "volume_storage_id": "volume_storage1",
            "description": "",
            "properties": {
                "size": "\"100 GB\"",
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
            'policy_id': 'policy_scale_sss-vnf-template',
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
                'name': 'opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'checksum': '',
                'disk_format': 'VMDK',
                'file_url': './zte-cn-sss-main-image/OMM/opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'
            },
            'image_file_id': 'opencos_sss_omm_img_release_20150723-1-disk1'
        },
        {
            'description': '',
            'properties': {
                'name': 'sss.vmdk',
                'checksum': '',
                'disk_format': 'VMDK',
                'file_url': './zte-cn-sss-main-image/NE/sss.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'
            },
            'image_file_id': 'sss'
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
                "cloud_type": "IaaS",
                "vl_profile": {"networkName": "test"},
                "connectivity_type": {}
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
                "function": "control",
                "protocol_data": [
                    {
                        "address_data": {
                            "l3_address_data": {
                                "fixed_ip_address": "test"
                            },
                        },
                    },
                ]

            },
            "vl_id": "vldId1",
            "vdu_id": "vdu1Id"
        }
    ],
    'local_storages': [

    ],
}
