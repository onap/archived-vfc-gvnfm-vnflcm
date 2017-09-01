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

from lcm.pub.config.config import AAI_BASE_URL, AAI_USER, AAI_PASSWORD
from lcm.pub.exceptions import NFLCMException
from lcm.pub.utils.restcall import call_req_aai, rest_no_auth

logger = logging.getLogger(__name__)

def call_aai(resource, method, data=''):
    return call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, method, data)

def create_ns(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "PUT", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Ns instance creation exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def delete_ns(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "DELETE", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "DELETE", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Ns instance delete exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def query_ns(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "GET", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "GET", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Ns instance query exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def create_vnf(vnf_id, data):
    resource = "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    ret = call_aai(resource, "PUT", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Vnf instance creation exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def delete_vnf(vnf_id, data=[]):
    resource = "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    ret = call_aai(resource, "DELETE", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "DELETE", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Vnf instance delete exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def query_vnf(vnf_id, data):
    resource = "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    ret = call_aai(resource, "GET", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "GET", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Vnf instance query exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def create_vserver(cloud_owner, cloud_region_id, tenant_id, vserver_id, data):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "PUT", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Vserver creation exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def delete_vserver(cloud_owner, cloud_region_id, tenant_id, vserver_id, data):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "DELETE", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "DELETE", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Vserver delete exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def query_vserver(cloud_owner, cloud_region_id, tenant_id, vserver_id, data):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "GET", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "GET", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Vserver query exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def put_vserver_relationship(cloud_owner, cloud_region_id, tenant_id, vserver_id, data):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s/relationship-list/relationship" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "PUT", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Put or update vserver relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def delete_vserver_relationship(cloud_owner, cloud_region_id, tenant_id, vserver_id, data):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s/relationship-list/relationship" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "DELETE", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "DELETE", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Delete vserver relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def put_vnf_relationship(vnf_id, data):
    resource = "/network/generic-vnfs/generic-vnf/%s/relationship-list/relationship" % vnf_id
    ret = call_aai(resource, "PUT", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Put or update vnf instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def delete_vnf_relationship(vnf_id, data):
    resource = "/network/generic-vnfs/generic-vnf/%s/relationship-list/relationship" % vnf_id
    ret = call_aai(resource, "DELETE", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "DELETE", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Delete vnf instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def put_ns_relationship(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s/relationship-list/relationship" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "PUT", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Put or update ns instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def delete_ns_relationship(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s/relationship-list/relationship" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "DELETE", data)
    # ret = call_req_aai(AAI_BASE_URL, AAI_USER, AAI_PASSWORD, rest_no_auth, resource, "DELETE", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NFLCMException("Delete ns instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])
