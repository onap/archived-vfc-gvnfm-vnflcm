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

import unittest
import json
from django.test import Client
from rest_framework import status

inst_res_url = "/api/vnflcm/v1/resources/inst"
term_res_url = "/api/vnflcm/v1/resources/term"
inst_res_data = {
    "vdus": [
        {
            "description": "",
            "vdu_id": "vdu_vNat",
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
            "nfv_compute": {
                "flavor_extra_specs": {
                },
                "mem_size": "2 GB",
                "num_cpus": 2
            },
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
                "name": "vNat_big_subnet",
                "network_name": "vNat_big",
                "is_predefined": False,
                "vendor": "zte",
                "netmask": "255.255.255.0",
                "mtu": 1500,
                "network_type": "vlan",
                "physical_network": "physnet1",
                "segmentation_id": "30",
                "vlan_transparent": False,
                "vds_name": "vds1",
                "cidr": "10.43.38.0/24",
                "ip_version": 4,
                "gateway_ip": "10.43.38.1",
                "dhcp_enabled": False,
                "start_ip": "10.43.38.2",
                "end_ip": "10.43.38.254",
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
                "ip_address": "10.43.38.253",
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
            "vdu_id": "vdu_vNat"
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
term_res_data = {
    "volume": [{"vim_id": "1", "tenant_id": "2", "res_id": "3"}],
    "network": [{"vim_id": "2", "tenant_id": "3", "res_id": "4"}],
    "subnet": [{"vim_id": "3", "tenant_id": "4", "res_id": "5"}],
    "port": [{"vim_id": "4", "tenant_id": "5", "res_id": "6"}],
    "flavor": [{"vim_id": "5", "tenant_id": "6", "res_id": "7"}],
    "vm": [{"vim_id": "6", "tenant_id": "7", "res_id": "8"}]
}


class SampleViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_sample(self):
        response = self.client.get("/samples/")
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.content)
        resp_data = json.loads(response.content)
        self.assertEqual({"status": "active"}, resp_data)

    def test_inst_res(self):
        resp = self.client.post(inst_res_url, data=json.dumps(inst_res_data), content_type='application/json')
        self.failUnlessEqual(status.HTTP_204_NO_CONTENT, resp.status_code)

    def test_term_res(self):
        resp = self.client.post(term_res_url, data=json.dumps(term_res_data), content_type='application/json')
        self.failUnlessEqual(status.HTTP_204_NO_CONTENT, resp.status_code)
