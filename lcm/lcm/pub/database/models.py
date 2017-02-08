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


class VnfInstModel(models.Model):
    class Meta:
        db_table = 'GVNFM_VNFINST'

    id = models.CharField(db_column='ID', primary_key=True, max_length=200)
    name = models.CharField(db_column='NAME', max_length=200)
    vnfd_id = models.CharField(db_column='VNFDID', max_length=200)
    description = models.CharField(db_column='DESCRIPTION', max_length=255, null=True, blank=True)
    status = models.CharField(db_column='STATUS', max_length=200, null=True, blank=True)
    create_time = models.CharField(db_column='CREATETIME', max_length=200, null=True, blank=True)
    lastuptime = models.CharField(db_column='LASTUPTIME', max_length=200, null=True, blank=True)

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
    descp = models.CharField(db_column='DESCP', max_length=1024)
    errcode = models.CharField(db_column='ERRCODE', max_length=255, null=True, blank=True)
    addtime = models.CharField(db_column='ADDTIME', max_length=255, null=True, blank=True)

    def toJSON(self):
        import json
        return json.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))
