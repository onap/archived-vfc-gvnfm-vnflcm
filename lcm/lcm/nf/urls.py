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

from django.conf.urls import url

from lcm.nf.views.curd_vnf_views import DeleteVnfAndQueryVnf, CreateVnfAndQueryVnfs
from lcm.nf.views.instantiate_vnf_view import InstantiateVnfView
from lcm.nf.views.terminate_vnf_view import TerminateVnfView
from lcm.nf.views.subscriptions_view import SubscriptionsView
from lcm.nf.views.subscriptions_view import SubscriptionDetailView
from lcm.nf.views.heal_vnf_view import HealVnfView
from lcm.nf.views.operate_vnf_view import OperateVnfView
from lcm.nf.views.scale_vnf_view import ScaleVnfView
from lcm.nf.views.scale_to_level_view import ScaleVnfToLevelView
from lcm.nf.views.change_ext_conn_view import ChangeExtConnView
from lcm.nf.views.change_vnf_flavour_view import ChangeVnfFlavourView
from lcm.nf.views.lcm_op_occs_view import QueryMultiVnfLcmOpOccs, QuerySingleVnfLcmOpOcc

urlpatterns = [
    url(r'^api/vnflcm/v1/subscriptions$', SubscriptionsView.as_view()),
    url(r'^api/vnflcm/v1/subscriptions/(?P<subscriptionid>[0-9a-zA-Z_-]+)$', SubscriptionDetailView.as_view()),
    url(r'^api/vnflcm/v1/vnf_instances$', CreateVnfAndQueryVnfs.as_view()),
    url(r'^api/vnflcm/v1/vnf_instances/(?P<instanceid>[0-9a-zA-Z_-]+)/instantiate$', InstantiateVnfView.as_view()),
    url(r'^api/vnflcm/v1/vnf_instances/(?P<instanceid>[0-9a-zA-Z_-]+)$', DeleteVnfAndQueryVnf.as_view()),
    url(r'^api/vnflcm/v1/vnf_instances/(?P<instanceid>[0-9a-zA-Z_-]+)/terminate$', TerminateVnfView.as_view()),
    url(r'^api/vnflcm/v1/vnf_instances/(?P<instanceid>[0-9a-zA-Z_-]+)/heal$', HealVnfView.as_view()),
    url(r'^api/vnflcm/v1/vnf_instances/(?P<instanceid>[0-9a-zA-Z_-]+)/operate$', OperateVnfView.as_view()),
    url(r'^api/vnflcm/v1/vnf_instances/(?P<instanceid>[0-9a-zA-Z_-]+)/scale$', ScaleVnfView.as_view()),
    url(r'^api/vnflcm/v1/vnf_instances/(?P<instanceid>[0-9a-zA-Z_-]+)/scale_to_level$', ScaleVnfToLevelView.as_view()),
    url(r'^api/vnflcm/v1/vnf_instances/(?P<instanceid>[0-9a-zA-Z_-]+)/change_flavour$', ChangeVnfFlavourView.as_view()),
    url(r'^api/vnflcm/v1/vnf_instances/(?P<instanceid>[0-9a-zA-Z_-]+)/change_ext_conn$', ChangeExtConnView.as_view()),
    url(r'^api/vnflcm/v1/vnf_lcm_op_occs$', QueryMultiVnfLcmOpOccs.as_view()),
    url(r'^api/vnflcm/v1/vnf_lcm_op_occs/(?P<lcmopoccid>[0-9a-zA-Z_-]+)$', QuerySingleVnfLcmOpOcc.as_view()),
]
