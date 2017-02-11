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
from django.db import models


class NfInstModel(models.Model):
    class Meta:
        db_table = 'NFINST'

    nfinstid = models.CharField(db_column='NFINSTID', max_length=200, primary_key=True)
    mnfinstid = models.CharField(db_column='M_NFINSTID', max_length=200, blank=True, null=True)
    nf_name = models.CharField(db_column='NFNAME', max_length=100, blank=True, null=True) #CreateVnfRequest.vnfInstanceName
    template_id = models.CharField(db_column='TEMPLATEID', max_length=200, blank=True, null=True)
    vnf_id = models.CharField(db_column='VNFID', max_length=200, blank=True, null=True)
    package_id = models.CharField(db_column='PACKAGEID', max_length=200, blank=True, null=True)
    vnfm_inst_id = models.CharField(db_column='VNFMINSTID', max_length=200, blank=True, null=True)
    multivim = models.IntegerField(db_column='MULTIVIM', default=0)
    ns_inst_id = models.CharField(db_column='NSINSTID', max_length=200, blank=True, null=True)
    status = models.CharField(db_column='STATUS', max_length=20, blank=True, null=True)
    flavour_id = models.CharField(db_column='FLAVOURID', max_length=200, blank=True, null=True) #InstantiateVnfRequest.flavourId
    vnf_level = models.CharField(db_column='VNFLEVEL', max_length=200, blank=True, null=True) #InstantiateVnfRequest.instantiationLevelId
    location = models.CharField(db_column='LOCATION', max_length=200, blank=True, null=True)
    deploy_environment = models.CharField(db_column='DEPLOYENVIRONMENT', max_length=100, blank=True, null=True)
    max_vm = models.IntegerField(db_column='MAXVM', blank=True, null=True)
    max_cpu = models.IntegerField(db_column='MAXCPU', blank=True, null=True)
    max_ram = models.IntegerField(db_column='MAXRAM', blank=True, null=True)
    max_hd = models.IntegerField(db_column='MAXHD', blank=True, null=True)
    max_shd = models.IntegerField(db_column='MAXSHD', blank=True, null=True)
    max_net = models.IntegerField(db_column='MAXNET', blank=True, null=True)
    version = models.CharField(db_column='VERSION', max_length=255, null=True)
    vendor = models.CharField(db_column='VENDOR', max_length=255, null=True, blank=True)
    producttype = models.CharField(db_column='PRODUCTTYPE', max_length=255, null=True)
    netype = models.CharField(db_column='NETYPE', max_length=255, null=True)
    vnfd_model = models.TextField(db_column='VNFDMODEL', max_length=20000, blank=True, null=True)
    input_params = models.TextField(db_column='INPUTPARAMS', max_length=2000, blank=True, null=True)  #InstantiateVnfRequest.additionalParams
    scale_params = models.TextField(db_column='SCALEPARAMS', max_length=2000, null=True, blank=True)
    create_time = models.CharField(db_column='CREATETIME', max_length=200, null=True, blank=True)
    lastuptime = models.CharField(db_column='LASTUPTIME', max_length=200, blank=True, null=True)
    extension = models.TextField(db_column='EXTENSION', max_length=65535, blank=True, null=True)
    initallocatedata = models.TextField(db_column='INITALLOCATEDATA', max_length=20000, blank=True, null=True)
    predefinedvm = models.TextField(db_column='PREDEFINEDVM', max_length=65535, blank=True, null=True)
    vnfextendtype = models.CharField(db_column='VNFEXTENDTYPE', max_length=255, null=True)

    instantiationState = models.CharField(db_column='INSTANTIATIONSTATE', max_length=200, blank=True, null=True)
    nf_desc = models.CharField(db_column='VNFINSTANCEDESC', max_length=200, blank=True, null=True)
    vnfdid = models.CharField(db_column='VNFDID', max_length=200, blank=True, null=True)
    vnfSoftwareVersion = models.CharField(db_column='VNFSOFTWAREVER', max_length=200, blank=True, null=True)
    vnfConfigurableProperties = models.TextField(db_column='VNFCONFIGURABLEPROPERTIES', max_length=20000, blank=True, null=True)
    localizationLanguage = models.CharField(db_column='LOCALIZATIONLANGUAGE', max_length=255, null=True)

class JobModel(models.Model):
    class Meta:
        db_table = 'JOB'

    _database = 'job'

    jobid = models.CharField(db_column='JOBID', primary_key=True, max_length=255)
    jobtype = models.CharField(db_column='JOBTYPE', max_length=255)
    jobaction = models.CharField(db_column='JOBACTION', max_length=255)
    resid = models.CharField(db_column='RESID', max_length=255)
    status = models.IntegerField(db_column='STATUS', null=True, blank=True)
    starttime = models.CharField(db_column='STARTTIME', max_length=255, null=True, blank=True)
    endtime = models.CharField(db_column='ENDTIME', max_length=255, null=True, blank=True)
    progress = models.IntegerField(db_column='PROGRESS', null=True, blank=True)
    user = models.CharField(db_column='USER', max_length=255, null=True, blank=True)
    parentjobid = models.CharField(db_column='PARENTJOBID', max_length=255, null=True, blank=True)
    resname = models.CharField(db_column='RESNAME', max_length=255, null=True, blank=True)

    def toJSON(self):
        import json
        return json.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))

class JobStatusModel(models.Model):
    class Meta:
        db_table = 'JOB_STATUS'

    _database = 'job'

    indexid = models.IntegerField(db_column='INDEXID')
    jobid = models.CharField(db_column='JOBID', max_length=255)
    status = models.CharField(db_column='STATUS', max_length=255)
    progress = models.IntegerField(db_column='PROGRESS', null=True, blank=True)
    descp = models.TextField(db_column='DESCP', max_length=1024)
    errcode = models.CharField(db_column='ERRCODE', max_length=255, null=True, blank=True)
    addtime = models.CharField(db_column='ADDTIME', max_length=255, null=True, blank=True)

    def toJSON(self):
        import json
        return json.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))

class NfvoRegInfoModel(models.Model):
    class Meta:
        db_table = 'NFVOREGINFO'

    nfvoid = models.CharField(max_length=255, primary_key=True, db_column='NFVOID')
    vnfminstid = models.CharField(max_length=255, db_column='VNFMINSTID')
    apiurl = models.CharField(max_length=255, db_column='URL')
    nfvouser = models.CharField(max_length=255, db_column='USERNAME', null=True)
    nfvopassword = models.CharField(max_length=255, db_column='PASSWD', null=True)
    authtype = models.IntegerField(db_column='AUTHTYPE', default=2)
    clientcert = models.CharField(max_length=255, db_column='CLIENTCERT', null=True)
    servercert = models.CharField(max_length=255, db_column='SERVERCERT', null=True)
    regtime = models.CharField(max_length=255, db_column='REGTIME')

class VmInstModel(models.Model):
    class Meta:
        db_table = 'VMINST'

    vmid = models.CharField(db_column='VMID', primary_key=True, max_length=255)
    vimid = models.CharField(db_column='VIMID', max_length=255)
    resouceid = models.CharField(db_column='RESOURCEID', max_length=255)
    insttype = models.IntegerField(db_column='INSTTYPE')
    instid = models.CharField(db_column='INSTID', max_length=255)
    vmname = models.CharField(db_column='VMNAME', max_length=255)
    operationalstate = models.IntegerField(db_column='OPERATIONALSTATE', null=True)
    zoneid = models.CharField(db_column='ZONEID', max_length=255, null=True)
    tenant = models.CharField(db_column='TENANT', max_length=255, null=True)
    hostid = models.CharField(db_column='HOSTID', max_length=255, null=True)
    detailinfo = models.TextField(db_column='DETAILINFO', max_length=8192, null=True)
    is_predefined = models.IntegerField(db_column='ISPREDEFINED', default=0, null=True)

class VNFCInstModel(models.Model):
    class Meta:
        db_table = 'VNFCINST'

    vnfcinstanceid = models.CharField(db_column='VNFCINSTANCEID', max_length=255, primary_key=True)
    vduid = models.CharField(db_column='VDUID', max_length=255)
    vdutype = models.CharField(db_column='VDUTYPE', max_length=255)
    nfinstid = models.CharField(db_column='NFINSTID', max_length=255)
    vmid = models.CharField(db_column='VMID', max_length=255)

class NetworkInstModel(models.Model):
    class Meta:
        db_table = 'NETWORKINST'

    networkid = models.CharField(db_column='NETWORKID', primary_key=True, max_length=255)
    vimid = models.CharField(db_column='VIMID', max_length=255)
    resouceid = models.CharField(db_column='RESOURCEID', max_length=255)
    insttype = models.IntegerField(db_column='INSTTYPE')
    instid = models.CharField(db_column='INSTID', max_length=255)
    name = models.CharField(db_column='NAME', max_length=255)
    tenant = models.CharField(db_column='TENANT', max_length=255, null=True)
    is_shared = models.IntegerField(db_column='ISSHARED', default=0, null=True)
    is_predefined = models.IntegerField(db_column='ISPREDEFINED', default=0, null=True)
    desc = models.CharField(db_column='DESC', max_length=255, null=True)
    vendor = models.CharField(db_column='VENDOR', max_length=255, null=True)
    bandwidth = models.IntegerField(db_column='BANDWIDTH', null=True)
    mtu = models.IntegerField(db_column='MTU', null=True)
    network_type = models.CharField(db_column='NETWORKTYPE', max_length=255, null=True)
    segmentid = models.CharField(db_column='SEGMENTID', max_length=255, null=True)
    vlantrans = models.IntegerField(db_column='VLANTRANS', null=True)
    networkqos = models.CharField(db_column='NETWORKQOS', max_length=255, null=True)


class SubNetworkInstModel(models.Model):
    class Meta:
        db_table = 'SUBNETWORKINST'

    subnetworkid = models.CharField(db_column='SUBNETWORKID', primary_key=True, max_length=255)
    vimid = models.CharField(db_column='VIMID', max_length=255)
    resouceid = models.CharField(db_column='RESOURCEID', max_length=255)
    networkid = models.CharField(db_column='NETWORKID', max_length=255)
    insttype = models.IntegerField(db_column='INSTTYPE')
    instid = models.CharField(db_column='INSTID', max_length=255)
    name = models.CharField(db_column='NAME', max_length=255)
    ipversion = models.IntegerField(db_column='IPVERSION', null=True)
    gatewayip = models.CharField(db_column='GATEWAYIP', max_length=255, null=True)
    isdhcpenabled = models.IntegerField(db_column='ISDHCPENABLED', null=True)
    cidr = models.CharField(db_column='CIDR', max_length=255)
    vdsname = models.CharField(db_column='VDSNAME', max_length=255, null=True)
    operationalstate = models.CharField(db_column='OPERATIONALSTATE', max_length=255, null=True)
    tenant = models.CharField(db_column='TENANT', max_length=255, null=True)
    is_predefined = models.IntegerField(db_column='ISPREDEFINED', default=0, null=True)

class VLInstModel(models.Model):
    class Meta:
        db_table = 'VLINST'

    vlinstanceid = models.CharField(db_column='VLINSTANCEID', max_length=255, primary_key=True)
    vldid = models.CharField(db_column='VLDID', max_length=255)
    vlinstancename = models.CharField(db_column='VLINSTANCENAME', max_length=255, blank=True, null=True)
    ownertype = models.IntegerField(db_column='OWNERTYPE')
    ownerid = models.CharField(db_column='OWNERID', max_length=255)
    relatednetworkid = models.CharField(db_column='RELATEDNETWORKID', max_length=255, blank=True, null=True)
    relatedsubnetworkid = models.CharField(db_column='RELATEDSUBNETWORKID', max_length=255, blank=True, null=True)
    vltype = models.IntegerField(db_column='VLTYPE', default=0)
    vimid = models.CharField(db_column='VIMID', max_length=255)
    tenant = models.CharField(db_column='TENANT', max_length=50)