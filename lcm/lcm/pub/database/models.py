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
    nf_name = models.CharField(db_column='NFNAME', max_length=100, blank=True, null=True)  # CreateVnfRequest.vnfInstanceName
    package_id = models.CharField(db_column='PACKAGEID', max_length=200, blank=True, null=True)
    status = models.CharField(db_column='STATUS', max_length=20, blank=True, null=True)
    flavour_id = models.CharField(db_column='FLAVOURID', max_length=200, blank=True, null=True)  # InstantiateVnfRequest.flavourId
    location = models.CharField(db_column='LOCATION', max_length=200, blank=True, null=True)
    version = models.CharField(db_column='VERSION', max_length=255, null=True)
    vendor = models.CharField(db_column='VENDOR', max_length=255, null=True, blank=True)
    netype = models.CharField(db_column='NETYPE', max_length=255, null=True)
    vnfd_model = models.TextField(db_column='VNFDMODEL', max_length=20000, blank=True, null=True)
    input_params = models.TextField(db_column='INPUTPARAMS', max_length=2000, blank=True, null=True)  # InstantiateVnfRequest.additionalParams
    create_time = models.CharField(db_column='CREATETIME', max_length=200, null=True, blank=True)
    lastuptime = models.CharField(db_column='LASTUPTIME', max_length=200, blank=True, null=True)

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


class StorageInstModel(models.Model):
    class Meta:
        db_table = 'STORAGEINST'

    storageid = models.CharField(db_column='STORAGEID', primary_key=True, max_length=255)
    vimid = models.CharField(db_column='VIMID', max_length=255)
    resouceid = models.CharField(db_column='RESOURCEID', max_length=255)
    insttype = models.IntegerField(db_column='INSTTYPE')
    instid = models.CharField(db_column='INSTID', max_length=255)
    name = models.CharField(db_column='NAME', max_length=255, null=True)
    storagetype = models.CharField(db_column='STORAGETYPE', max_length=255)
    size = models.CharField(db_column='SIZE', max_length=255)
    # rdmaenabled = models.IntegerField(db_column='RDMAENABLED', null=True)
    # disktype = models.CharField(db_column='DISKTYPE', max_length=255)
    # ownerid = models.CharField(db_column='OWNERID', max_length=255, null=True)
    # zoneid = models.CharField(db_column='ZONEID', max_length=255, null=True)
    # hostid = models.CharField(db_column='HOSTID', max_length=255, null=True)
    # operationalstate = models.CharField(db_column='OPERATIONALSTATE', max_length=255, null=True)
    tenant = models.CharField(db_column='TENANT', max_length=50, null=True)
    is_predefined = models.IntegerField(db_column='ISPREDEFINED', default=0, null=True)
    create_time = models.CharField(db_column='CREATETIME', max_length=200, null=True, blank=True)
    nodeId = models.CharField(db_column='NODEID', max_length=255, null=True)


class VmInstModel(models.Model):
    class Meta:
        db_table = 'VMINST'

    vmid = models.CharField(db_column='VMID', primary_key=True, max_length=255)
    vimid = models.CharField(db_column='VIMID', max_length=255)
    tenant = models.CharField(db_column='TENANT', max_length=255, null=True)
    resouceid = models.CharField(db_column='RESOURCEID', max_length=255)
    vmname = models.CharField(db_column='VMNAME', max_length=255)
    nic_array = models.CharField(db_column='NICARRAY', max_length=255)
    metadata = models.CharField(db_column='METADATA', max_length=255)
    volume_array = models.CharField(db_column='VOLUMEARRAY', max_length=255)
    server_group = models.CharField(db_column='SERVERGROUP', max_length=255)
    availability_zone = models.CharField(db_column='AVAILABILITYZONE', max_length=255)
    flavor_id = models.CharField(db_column='FLAVORID', max_length=255)
    security_groups = models.CharField(db_column='SECURITYGROUPS', max_length=255)
    operationalstate = models.CharField(db_column='OPERATIONALSTATE', max_length=255, null=True)
    insttype = models.IntegerField(db_column='INSTTYPE')
    is_predefined = models.IntegerField(db_column='ISPREDEFINED', default=0, null=True)
    create_time = models.CharField(db_column='CREATETIME', max_length=200, null=True, blank=True)
    instid = models.CharField(db_column='INSTID', max_length=255)
    nodeId = models.CharField(db_column='NODEID', max_length=255, null=True)


class VNFCInstModel(models.Model):
    class Meta:
        db_table = 'VNFCINST'

    vnfcinstanceid = models.CharField(db_column='VNFCINSTANCEID', max_length=255, primary_key=True)
    vduid = models.CharField(db_column='VDUID', max_length=255)
    vdutype = models.CharField(db_column='VDUTYPE', max_length=255)
    instid = models.CharField(db_column='NFINSTID', max_length=255)
    vmid = models.CharField(db_column='VMID', max_length=255)
    is_predefined = models.IntegerField(db_column='ISPREDEFINED', default=0, null=True)


class FlavourInstModel(models.Model):
    class Meta:
        db_table = 'FLAVOURINST'

    flavourid = models.CharField(db_column='FLAVOURID', max_length=255, primary_key=True)
    vimid = models.CharField(db_column='VIMID', max_length=255)
    resouceid = models.CharField(db_column='RESOURCEID', max_length=255)
    name = models.CharField(db_column='NAME', max_length=255)
    tenant = models.CharField(db_column='TENANT', max_length=255, null=True)
    vcpu = models.IntegerField(db_column='VCPU', null=True)
    memory = models.IntegerField(db_column='MEMORY', null=True)
    disk = models.IntegerField(db_column='DISK', null=True)
    ephemeral = models.IntegerField(db_column='EPHEMERAL', null=True)
    swap = models.IntegerField(db_column='SWAP', null=True)
    isPublic = models.IntegerField(db_column='ISPUBLIC', null=True)
    extraspecs = models.TextField(db_column='EXTRASPECS', max_length=4096)
    instid = models.CharField(db_column='INSTID', max_length=255)
    create_time = models.CharField(db_column='CREATETIME', max_length=200, null=True, blank=True)
    is_predefined = models.IntegerField(db_column='ISPREDEFINED', default=0, null=True)


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
    is_predefined = models.IntegerField(db_column='ISPREDEFINED', default=0, null=True)
    desc = models.CharField(db_column='DESC', max_length=255, null=True)
    vendor = models.CharField(db_column='VENDOR', max_length=255, null=True)
    bandwidth = models.IntegerField(db_column='BANDWIDTH', null=True)
    mtu = models.IntegerField(db_column='MTU', null=True)
    network_type = models.CharField(db_column='NETWORKTYPE', max_length=255, null=True)
    segmentid = models.CharField(db_column='SEGMENTID', max_length=255, null=True)
    networkqos = models.CharField(db_column='NETWORKQOS', max_length=255, null=True)
    create_time = models.CharField(db_column='CREATETIME', max_length=200, null=True, blank=True)
    physicalNetwork = models.CharField(db_column='PHYNETWORK', max_length=255, null=True)
    is_shared = models.IntegerField(db_column='ISSHARED', default=0, null=True)
    vlantrans = models.IntegerField(db_column='VLANTRANS', null=True)
    routerExternal = models.IntegerField(db_column='ROUTEREXTERNAL', default=0, null=True)
    nodeId = models.CharField(db_column='NODEID', max_length=255, null=True)


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
    create_time = models.CharField(db_column='CREATETIME', max_length=200, null=True, blank=True)
    dnsNameservers = models.TextField(db_column='DNSNAMESERVERS', max_length=1024)
    hostRoutes = models.TextField(db_column='HOSTROUTES', max_length=1024)
    allocationPools = models.TextField(db_column='ALLOCATIONPOOLS', max_length=1024)


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


class PortInstModel(models.Model):
    class Meta:
        db_table = 'PORTINST'

    portid = models.CharField(db_column='PORTID', primary_key=True, max_length=255)
    networkid = models.CharField(db_column='NETWORKID', max_length=255)
    subnetworkid = models.CharField(db_column='SUBNETWORKID', max_length=255, null=True)
    vimid = models.CharField(db_column='VIMID', max_length=255)
    resouceid = models.CharField(db_column='RESOURCEID', max_length=255)
    name = models.CharField(db_column='NAME', max_length=255, null=True)
    insttype = models.IntegerField(db_column='INSTTYPE')
    instid = models.CharField(db_column='INSTID', max_length=255)
    cpinstanceid = models.CharField(db_column='CPINSTANCEID', max_length=255, null=True)
    bandwidth = models.CharField(db_column='BANDWIDTH', max_length=255, null=True)
    operationalstate = models.CharField(db_column='OPERATIONALSTATE', max_length=255, null=True)
    ipaddress = models.CharField(db_column='IPADDRESS', max_length=255)
    macaddress = models.CharField(db_column='MACADDRESS', max_length=255)
    nicorder = models.CharField(db_column='NICORDER', max_length=255)
    floatipaddress = models.CharField(db_column='FLOATIPADDRESS', max_length=255, null=True)
    serviceipaddress = models.CharField(db_column='SERVICEIPADDRESS', max_length=255, null=True)
    typevirtualnic = models.CharField(db_column='TYPEVIRTUALNIC', max_length=255, null=True)
    sfcencapsulation = models.CharField(db_column='SFCENCAPSULATION', max_length=255, null=True)
    direction = models.CharField(db_column='DIRECTION', max_length=255, null=True)
    tenant = models.CharField(db_column='TENANT', max_length=255, null=True)
    interfacename = models.CharField(db_column='INTERFACENAME', max_length=255, blank=True, null=True)
    vmid = models.CharField(db_column='VMID', max_length=255, blank=True, null=True)
    create_time = models.CharField(db_column='CREATETIME', max_length=200, null=True, blank=True)
    securityGroups = models.CharField(db_column='SECURITYGROUPS', max_length=255)
    is_predefined = models.IntegerField(db_column='ISPREDEFINED', default=0, null=True)
    nodeId = models.CharField(db_column='NODEID', max_length=255, null=True)


class CPInstModel(models.Model):
    class Meta:
        db_table = 'CPINST'

    cpinstanceid = models.CharField(db_column='CPINSTANCEID', max_length=255, primary_key=True)
    cpdid = models.CharField(db_column='CPDID', max_length=255)
    cpinstancename = models.CharField(db_column='CPINSTANCENAME', max_length=255)
    vlinstanceid = models.CharField(db_column='VLINSTANCEID', max_length=255)
    ownertype = models.IntegerField(db_column='OWNERTYPE')
    ownerid = models.CharField(db_column='OWNERID', max_length=255)
    relatedtype = models.IntegerField(db_column='RELATEDTYPE')
    relatedvl = models.CharField(db_column='RELATEDVL', max_length=255, blank=True, null=True)
    relatedcp = models.CharField(db_column='RELATEDCP', max_length=255, blank=True, null=True)
    relatedport = models.CharField(db_column='RELATEDPORT', max_length=255, blank=True, null=True)
