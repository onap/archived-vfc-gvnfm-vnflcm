-- Copyright (c) 2019, CMCC Technologies Co., Ltd.
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

use gvnfm;

CREATE TABLE `NFINST` (
    `NFINSTID` varchar(200) NOT NULL PRIMARY KEY,
    `NFNAME` varchar(100),
    `VNFMINSTID` varchar(255),
    `PACKAGEID` varchar(200),
    `STATUS` varchar(20),
    `FLAVOURID` varchar(200),
    `LOCATION` varchar(200),
    `VERSION` varchar(255),
    `VENDOR` varchar(255),
    `NETYPE` varchar(255),
    `VNFDMODEL` longtext,
    `INPUTPARAMS` longtext,
    `CREATETIME` varchar(200),
    `LASTUPTIME` varchar(200),
    `VNFINSTANCEDESC` varchar(200),
    `VNFDID` varchar(200),
    `VNFSOFTWAREVER` varchar(200),
    `VNFCONFIGURABLEPROPERTIES` longtext,
    `LOCALIZATIONLANGUAGE` varchar(255),
    `OPERATIONSTATE` varchar(255),
    `RESINFO` longtext,
    `VIMINFO` longtext
)
;
CREATE TABLE `JOB` (
    `JOBID` varchar(255) NOT NULL PRIMARY KEY,
    `JOBTYPE` varchar(255) NOT NULL,
    `JOBACTION` varchar(255) NOT NULL,
    `RESID` varchar(255) NOT NULL,
    `STATUS` integer,
    `STARTTIME` varchar(255),
    `ENDTIME` varchar(255),
    `PROGRESS` integer,
    `USER` varchar(255),
    `PARENTJOBID` varchar(255),
    `RESNAME` varchar(255)
)
;
CREATE TABLE `JOB_STATUS` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `INDEXID` integer NOT NULL,
    `JOBID` varchar(255) NOT NULL,
    `STATUS` varchar(255) NOT NULL,
    `PROGRESS` integer,
    `DESCP` longtext NOT NULL,
    `ERRCODE` varchar(255),
    `ADDTIME` varchar(255)
)
;
CREATE TABLE `NFVOREGINFO` (
    `NFVOID` varchar(255) NOT NULL PRIMARY KEY,
    `VNFMINSTID` varchar(255) NOT NULL,
    `URL` varchar(255) NOT NULL,
    `USERNAME` varchar(255),
    `PASSWD` varchar(255),
    `AUTHTYPE` integer NOT NULL,
    `CLIENTCERT` varchar(255),
    `SERVERCERT` varchar(255),
    `REGTIME` varchar(255) NOT NULL
)
;
CREATE TABLE `STORAGEINST` (
    `STORAGEID` varchar(255) NOT NULL PRIMARY KEY,
    `VIMID` varchar(255) NOT NULL,
    `RESOURCEID` varchar(255) NOT NULL,
    `INSTTYPE` integer NOT NULL,
    `INSTID` varchar(255) NOT NULL,
    `NAME` varchar(255),
    `STORAGETYPE` varchar(255) NOT NULL,
    `SIZE` varchar(255) NOT NULL,
    `TENANT` varchar(50),
    `ISPREDEFINED` integer,
    `CREATETIME` varchar(200),
    `NODEID` varchar(255)
)
;
CREATE TABLE `VMINST` (
    `VMID` varchar(255) NOT NULL PRIMARY KEY,
    `VIMID` varchar(255) NOT NULL,
    `TENANT` varchar(255),
    `RESOURCEID` varchar(255) NOT NULL,
    `VMNAME` varchar(255) NOT NULL,
    `NICARRAY` varchar(255) NOT NULL,
    `METADATA` varchar(255) NOT NULL,
    `VOLUMEARRAY` varchar(255) NOT NULL,
    `SERVERGROUP` varchar(255) NOT NULL,
    `AVAILABILITYZONE` varchar(255) NOT NULL,
    `FLAVORID` varchar(255) NOT NULL,
    `SECURITYGROUPS` varchar(255) NOT NULL,
    `OPERATIONALSTATE` varchar(255),
    `INSTTYPE` integer NOT NULL,
    `ISPREDEFINED` integer,
    `CREATETIME` varchar(200),
    `INSTID` varchar(255) NOT NULL,
    `NODEID` varchar(255)
)
;
CREATE TABLE `VNFCINST` (
    `VNFCINSTANCEID` varchar(255) NOT NULL PRIMARY KEY,
    `VDUID` varchar(255) NOT NULL,
    `VDUTYPE` varchar(255) NOT NULL,
    `NFINSTID` varchar(255) NOT NULL,
    `VMID` varchar(255) NOT NULL,
    `ISPREDEFINED` integer
)
;
CREATE TABLE `FLAVOURINST` (
    `FLAVOURID` varchar(255) NOT NULL PRIMARY KEY,
    `VIMID` varchar(255) NOT NULL,
    `RESOURCEID` varchar(255) NOT NULL,
    `NAME` varchar(255) NOT NULL,
    `TENANT` varchar(255),
    `VCPU` integer,
    `MEMORY` integer,
    `DISK` integer,
    `EPHEMERAL` integer,
    `SWAP` integer,
    `ISPUBLIC` integer,
    `EXTRASPECS` varchar(255) NOT NULL,
    `INSTID` varchar(255) NOT NULL,
    `CREATETIME` varchar(200),
    `ISPREDEFINED` integer
)
;
CREATE TABLE `NETWORKINST` (
    `NETWORKID` varchar(255) NOT NULL PRIMARY KEY,
    `VIMID` varchar(255) NOT NULL,
    `RESOURCEID` varchar(255) NOT NULL,
    `INSTTYPE` integer NOT NULL,
    `INSTID` varchar(255) NOT NULL,
    `NAME` varchar(255) NOT NULL,
    `TENANT` varchar(255),
    `ISPREDEFINED` integer,
    `DESC` varchar(255),
    `VENDOR` varchar(255),
    `BANDWIDTH` integer,
    `MTU` integer,
    `NETWORKTYPE` varchar(255),
    `SEGMENTID` varchar(255),
    `NETWORKQOS` varchar(255),
    `CREATETIME` varchar(200),
    `PHYNETWORK` varchar(255),
    `ISSHARED` integer,
    `VLANTRANS` integer,
    `ROUTEREXTERNAL` integer,
    `NODEID` varchar(255)
)
;
CREATE TABLE `SUBNETWORKINST` (
    `SUBNETWORKID` varchar(255) NOT NULL PRIMARY KEY,
    `VIMID` varchar(255) NOT NULL,
    `RESOURCEID` varchar(255) NOT NULL,
    `NETWORKID` varchar(255) NOT NULL,
    `INSTTYPE` integer NOT NULL,
    `INSTID` varchar(255) NOT NULL,
    `NAME` varchar(255) NOT NULL,
    `IPVERSION` integer,
    `GATEWAYIP` varchar(255),
    `ISDHCPENABLED` integer,
    `CIDR` varchar(255) NOT NULL,
    `VDSNAME` varchar(255),
    `OPERATIONALSTATE` varchar(255),
    `TENANT` varchar(255),
    `ISPREDEFINED` integer,
    `CREATETIME` varchar(200),
    `DNSNAMESERVERS` longtext NOT NULL,
    `HOSTROUTES` longtext NOT NULL,
    `ALLOCATIONPOOLS` longtext NOT NULL
)
;
CREATE TABLE `VLINST` (
    `VLINSTANCEID` varchar(255) NOT NULL PRIMARY KEY,
    `VLDID` varchar(255) NOT NULL,
    `VLINSTANCENAME` varchar(255),
    `OWNERTYPE` integer NOT NULL,
    `OWNERID` varchar(255) NOT NULL,
    `RELATEDNETWORKID` varchar(255),
    `RELATEDSUBNETWORKID` varchar(255),
    `VLTYPE` integer NOT NULL,
    `VIMID` varchar(255) NOT NULL,
    `TENANT` varchar(50) NOT NULL
)
;
CREATE TABLE `PORTINST` (
    `PORTID` varchar(255) NOT NULL PRIMARY KEY,
    `NETWORKID` varchar(255) NOT NULL,
    `SUBNETWORKID` varchar(255),
    `VIMID` varchar(255) NOT NULL,
    `RESOURCEID` varchar(255) NOT NULL,
    `NAME` varchar(255),
    `INSTTYPE` integer NOT NULL,
    `INSTID` varchar(255) NOT NULL,
    `CPINSTANCEID` varchar(255),
    `BANDWIDTH` varchar(255),
    `OPERATIONALSTATE` varchar(255),
    `IPADDRESS` varchar(255) NOT NULL,
    `MACADDRESS` varchar(255) NOT NULL,
    `NICORDER` varchar(255) NOT NULL,
    `FLOATIPADDRESS` varchar(255),
    `SERVICEIPADDRESS` varchar(255),
    `TYPEVIRTUALNIC` varchar(255),
    `SFCENCAPSULATION` varchar(255),
    `DIRECTION` varchar(255),
    `TENANT` varchar(255),
    `INTERFACENAME` varchar(255),
    `VMID` varchar(255),
    `CREATETIME` varchar(200),
    `SECURITYGROUPS` varchar(255) NOT NULL,
    `ISPREDEFINED` integer,
    `NODEID` varchar(255)
)
;
CREATE TABLE `CPINST` (
    `CPINSTANCEID` varchar(255) NOT NULL PRIMARY KEY,
    `CPDID` varchar(255) NOT NULL,
    `CPINSTANCENAME` varchar(255) NOT NULL,
    `VLINSTANCEID` varchar(255) NOT NULL,
    `OWNERTYPE` integer NOT NULL,
    `OWNERID` varchar(255) NOT NULL,
    `RELATEDTYPE` integer NOT NULL,
    `RELATEDVL` varchar(255),
    `RELATEDCP` varchar(255),
    `RELATEDPORT` varchar(255)
)
;
CREATE TABLE `VNF_REG` (
    `ID` varchar(200) NOT NULL PRIMARY KEY,
    `IP` varchar(200) NOT NULL,
    `PORT` varchar(200) NOT NULL,
    `USERNAME` varchar(255) NOT NULL,
    `PASSWORD` varchar(255) NOT NULL
)
;
CREATE TABLE `SUBSCRIPTION` (
    `SUBSCRIPTIONID` varchar(200) NOT NULL PRIMARY KEY,
    `CALLBACKURI` longtext NOT NULL,
    `AUTHINFO` longtext,
    `NOTIFICATIONTYPES` varchar(255),
    `OPERATIONTYPES` longtext,
    `OPERATIONSTATES` longtext,
    `VNFINSTANCEFILTER` longtext,
    `LINKS` longtext NOT NULL
)
;
CREATE TABLE `VNFLCMOPOCCS` (
    `ID` varchar(255) NOT NULL PRIMARY KEY,
    `OPERATIONSTATE` varchar(30) NOT NULL,
    `STATEENTEREDTIME` varchar(30) NOT NULL,
    `STARTTIME` varchar(30) NOT NULL,
    `VNFINSTANCEID` varchar(255) NOT NULL,
    `GRANTID` varchar(255),
    `OPERATION`  varchar(30) NOT NULL,
    `ISAUTOMATICINVOCATION` varchar(5) NOT NULL,
    `OPERATIONPARAMS` longtext NOT NULL,
    `ISCANCELPENDING` varchar(5) NOT NULL,
    `CANCELMODE` varchar(255),
    `ERROR` longtext,
    `RESOURCECHANGES` longtext,
    `CHANGEDINFO` longtext,
    `CHANGEDEXTCONNECTIVITY` longtext,
    `LINKS` longtext NOT NULL
)
;
COMMIT;
