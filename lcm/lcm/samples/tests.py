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

import mock
import unittest
import json
from rest_framework.test import APIClient
from rest_framework import status
from lcm.pub.utils import restcall

inst_res_url = "/api/vnflcm/v1/resources/inst"
term_res_url = "/api/vnflcm/v1/resources/term"
inst_res_data = {
    "vdus": [
        {
            "type": "tosca.nodes.nfv.Vdu.Compute",
            "description": "vbng",
            "vdu_id": "VDU_vbng_0",
            "virtual_compute": {
                "virtual_memory": {
                    "virtual_mem_size": "4096 MB",
                    "vdu_memory_requirements": {
                        "memoryPageSize": "2 MB",
                        "numberOfPages": "1024"
                    }
                },
                "virtual_cpu": {
                    "num_virtual_cpu": "2",
                    "cpu_architecture": "generic"
                },
                "virtual_storage": {
                    "type_of_storage": "root",
                    "size_of_storage": "40 GB"
                },
            },
            "artifacts": [
                {
                    "artifact_name": "cirros.img",
                    "type": "tosca.artifacts.nfv.SwImage",
                    "properties": {
                        "operating_system": "unbant",
                        "sw_image": "/swimages/xenial-snat.qcow2",
                        "name": "cirros.img",
                        "checksum": "5000",
                        "min_ram": "1 GB",
                        "disk_format": "qcow2",
                        "version": "1.0",
                        "container_format": "bare",
                        "min_disk": "10 GB",
                        "size": "10 GB"
                    },
                    "file": "/swimages/xenial-snat.qcow2"
                }
            ],
            "image_file": "cirros.img",
            "local_storages": [
                "intel_local_storages_1"
            ],
            "dependencies": [
            ],
            "vls": [
                "vl_vNat"
            ],
            "cps": [
                "cp_vNat"
            ],
            "properties": {
                "configurable_properties": {
                    "test": {
                        "additional_vnfc_configurable_properties": {
                            "aaa": "1"
                        }
                    }
                },
                "name": "vNat",
                "location_info": {
                    "vimid": "f1e33529-4a88-4155-9d7a-893cf2c80527",
                    "tenant": "vnfm",
                    "availability_zone": "zone1",
                    "host": "host1"
                },
                "descrption": "the virtual machine of vNat",
                "boot_order": [
                    "vNAT_Storage"
                ]
            }
        }
    ],
    "volume_storages": [
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
                    "vimid": "f1e33529-4a88-4155-9d7a-893cf2c80527",
                    "tenant": "vnfm",
                    "availability_zone": "zone1"
                },
                "is_predefined": False,
                "is_shared": False,
            },
            "image_file": [
                "volume_image"
            ]
        }
    ],
    "local_storages": [
        {
            "local_storage_id": "omp_local_disk1",
            "description": "",
            "properties": {
                "size": "100 GB",
                "disk_type": "root",
            },
        }
    ],
    "routers": [
    ],
    "image_files": [
        {
            "description": "",
            "properties": {
                "operating_system": "unbant",
                "sw_image": "/swimages/xenial-snat.qcow2",
                "name": "cirros.img",
                "checksum": "5000",
                "min_ram": "1 GB",
                "disk_format": "qcow2",
                "version": "1.0",
                "container_format": "bare",
                "min_disk": "10 GB",
                "size": "10 GB"
            },
            "image_file_id": "cirros.img"
        }
    ],
    "vnf_exposed": {
        "external_cps": [
            {
                "key_name": "sriov_plane",
                "cp_id": "SRIOV_Port"
            }
        ],
        "forward_cps": [
        ]
    },
    'vls': [
        {
            "vl_id": "vl_vNat",
            "description": "",
            "properties": {
                "connectivity_type": {
                    "layer_protocol": "ipv4"
                },
                "vl_profile": {
                    "networkName": "vNat_big",
                    "networkType": "vlan",
                    "physicalNetwork": "physnet1",
                    "segmentationId": "30",
                    "vlanTransparent": False,
                    "cidr": "10.43.38.0/24",
                    "gatewayIp": "10.43.38.1",
                    "dhcpEnabled": False,
                    "startIp": "10.43.38.2",
                    "endIp": "10.43.38.254"
                },
                "is_predefined": False,
                "vendor": "zte",
                "netmask": "255.255.255.0",
                "mtu": 1500,
                "vds_name": "vds1",
                "host_routes": [
                    {
                        "destination": "10.43.26.0/24",
                        "nexthop": "10.41.23.1"
                    }
                ],
                "location_info": {
                    "vimid": "f1e33529-4a88-4155-9d7a-893cf2c80527",
                    "tenant": "vnfm"
                },
                "cloud_type": "IaaS"
            },
            "route_id": "router01",
            "route_external": False
        }
    ],
    "cps": [
        {

            "properties": {
                "name": "vNat_big_subnet_port",
                "protocol_data": {
                    "address_data": {
                        "l3_address_data": {
                            "fixed_ip_address": "10.43.38.253"
                        },
                    },
                },
                "vnic_type": "normal",
                "role": "root",
                "virtual_network_interface_requirements": [
                    {
                        "requirement": {
                            "SRIOV": "true"
                        },
                        "support_mandatory": False,
                        "name": "sriov",
                        "description": "sriov"
                    }
                ],
                "layer_protocol": "ipv4",
                "description": "sriov port"
            },
            "vl_id": "vl_vNat",
            "description": "",
            "cp_id": "cp_vNat",
            "vdu_id": "VDU_vbng_0"
        }
    ],
    "metadata": {
        "vnfSoftwareVersion": "1.0.0",
        "vnfmType": "gvnfmdriver",
        "vnfProductName": "openNAT",
        "localizationLanguage": "[english, chinese]",
        "vnfProvider": "intel",
        "vnfmInfo": "GVNFM",
        "defaultLocalizationLanguage": "english",
        "csarVersion": "1.0.0",
        "vnfdId": "openNAT-1.0",
        "csarProvider": "intel",
        "vnfProductInfoDescription": "openNAT",
        "version": "1.0.0",
        "vnfdVersion": "1.0.0",
        "vnfProductInfoName": "openNAT",
        "vendor": "intel",
        "csarType": "NFAR",
        "id": "openNAT-1.0"
    }
}
NOT_PREDEFINED = 1
term_res_data = {
    "volume": [{"is_predefined": NOT_PREDEFINED, "vim_id": "1", "tenant_id": "2", "res_id": "3"}],
    "network": [{"is_predefined": NOT_PREDEFINED, "vim_id": "2", "tenant_id": "3", "res_id": "4"}],
    "subnet": [{"is_predefined": NOT_PREDEFINED, "vim_id": "3", "tenant_id": "4", "res_id": "5"}],
    "port": [{"is_predefined": NOT_PREDEFINED, "vim_id": "4", "tenant_id": "5", "res_id": "6"}],
    "flavor": [{"is_predefined": NOT_PREDEFINED, "vim_id": "5", "tenant_id": "6", "res_id": "7"}],
    "vm": [{"is_predefined": NOT_PREDEFINED, "vim_id": "6", "tenant_id": "7", "res_id": "8"}]
}


c0_data_get_tenant_id = {
    "tenants": [
        {
            "id": "1",
            "name": "vnfm",
        }
    ]
}

c1_data_create_volume = {
    "vimId": "f1e33529-4a88-4155-9d7a-893cf2c80527",
    "nodeId": "",
    "id": "234",
    "name": "volume1"
}

c1_data_get_volume = {
    "vimId": "f1e33529-4a88-4155-9d7a-893cf2c80527",
    "status": "AVAILABLE"
}

c2_data_create_network = {
    "vimId": "f1e33529-4a88-4155-9d7a-893cf2c80527",
    "nodeId": "",
    "id": "234"
}

c3_data_create_subnet = {
    "vimId": "f1e33529-4a88-4155-9d7a-893cf2c80527",
    "id": "345"
}

c4_data_create_port = {
    "vimId": "f1e33529-4a88-4155-9d7a-893cf2c80527",
    "nodeId": "",
    "id": "456"
}

c5_data_get_flavor = [{
    "flavors": {
        "flavor": [
            {
                "flavor-id": "111111",
                "hpa-capabilities": [
                    {
                        "hpa-capability-id": "1243",
                        "hpa-feature-attributes": [
                            {
                                "hpa-attribute-key": "memoryPageSize",
                                "hpa-attribute-value": {"value": 2, "unit": "MB"}
                            }
                        ]
                    }
                ]
            }
        ]
    }
}]

c6_data_list_image = {
    "images": [
        {
            "name": "cirros.img",
            "id": "678"
        }
    ]
}

c6_data_create_vm = {
    "id": "789",
    "name": "vm"
}

c6_data_get_vm = {
    "id": "789",
    "status": "Active",
    "name": "vm"
}


class SampleViewTest(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        pass

    def test_sample(self):
        response = self.client.get("/samples/")
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.content)
        resp_data = json.loads(response.content)
        self.assertEqual({"status": "active"}, resp_data)

    @mock.patch.object(restcall, 'call_req')
    def test_inst_res(self, mock_call_req):
        r0_data_get_tenant_id = [0, json.JSONEncoder().encode(c0_data_get_tenant_id), '200']
        r1_data_create_volume = [0, json.JSONEncoder().encode(c1_data_create_volume), '200']
        r1_data_get_volume = [0, json.JSONEncoder().encode(c1_data_get_volume), '200']
        r2_data_create_network = [0, json.JSONEncoder().encode(c2_data_create_network), '200']
        r3_data_create_subnet = [0, json.JSONEncoder().encode(c3_data_create_subnet), '200']
        r4_data_create_port = [0, json.JSONEncoder().encode(c4_data_create_port), '200']
        r5_data_get_flavor = [0, json.JSONEncoder().encode(c5_data_get_flavor), '200']
        r6_data_list_image = [0, json.JSONEncoder().encode(c6_data_list_image), '200']
        r6_data_create_vm = [0, json.JSONEncoder().encode(c6_data_create_vm), '200']
        r6_data_get_vm = [0, json.JSONEncoder().encode(c6_data_get_vm), '200']

        mock_call_req.side_effect = [r0_data_get_tenant_id,
                                     r1_data_create_volume, r1_data_get_volume,
                                     r2_data_create_network,
                                     r3_data_create_subnet,
                                     r4_data_create_port,
                                     r5_data_get_flavor,
                                     r6_data_list_image, r6_data_create_vm, r6_data_get_vm]
        resp = self.client.post(inst_res_url, data=json.dumps(inst_res_data), content_type='application/json')
        self.failUnlessEqual(status.HTTP_204_NO_CONTENT, resp.status_code)

    @mock.patch.object(restcall, 'call_req')
    def test_term_res(self, mock_call_req):
        r0_data_delete = [0, json.JSONEncoder().encode({"vim_id": "123"}), '200']
        mock_call_req.side_effect = [r0_data_delete,
                                     r0_data_delete,
                                     r0_data_delete,
                                     r0_data_delete,
                                     r0_data_delete,
                                     r0_data_delete,
                                     r0_data_delete]
        resp = self.client.post(term_res_url, data=json.dumps(term_res_data), content_type='application/json')
        self.failUnlessEqual(status.HTTP_204_NO_CONTENT, resp.status_code)
