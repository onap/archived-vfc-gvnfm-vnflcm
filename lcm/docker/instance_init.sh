#!/bin/bash

#
# Copyright (c) 2019, CMCC Technologies Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

pip install PyMySQL==0.9.3
if [ ! -f /service/vfc/gvnfm/vnflcm/lcm/resources/bin/logs/django.log ]; then
    mkdir -p /service/vfc/gvnfm/vnflcm/lcm/resources/bin/logs/
    touch /service/vfc/gvnfm/vnflcm/lcm/resources/bin/logs/django.log
else
    echo >/service/vfc/gvnfm/vnflcm/lcm/resources/bin/logs/django.log
fi

if [ ! -f /var/log/onap/vfc/gvnfm-vnflcm/runtime_lcm.log ]; then
    mkdir -p /var/log/onap/vfc/gvnfm-vnflcm/
    touch /var/log/onap/vfc/gvnfm-vnflcm/runtime_lcm.log
else
    echo >/var/log/onap/vfc/gvnfm-vnflcm/runtime_lcm.log
fi

MYSQL_IP=`echo $MYSQL_ADDR | cut -d: -f 1`
MYSQL_PORT=`echo $MYSQL_ADDR | cut -d: -f 2`
MYSQL_USER=`echo $MYSQL_AUTH | cut -d: -f 1`
MYSQL_ROOT_PASSWORD=`echo $MYSQL_AUTH | cut -d: -f 2`

function create_database {
    cd /service/vfc/gvnfm/vnflcm/lcm/resources/bin
    bash initDB.sh $MYSQL_USER $MYSQL_ROOT_PASSWORD $MYSQL_PORT $MYSQL_IP

    man_path=/service/vfc/gvnfm/vnflcm/lcm
    tab=`mysql -u${MYSQL_USER} -p${MYSQL_ROOT_PASSWORD} -P${MYSQL_PORT} -h${MYSQL_IP} -e "SELECT count(TABLE_NAME) FROM information_schema.TABLES WHERE TABLE_SCHEMA='gvnfm';"`
    tab1=`echo $tab |awk '{print $2}'`

    if [ $tab1 -eq 0 ] ; then

        echo "TABLE NOT EXISTS, START MIGRATE"
        python $man_path/manage.py makemigrations && python $man_path/manage.py migrate &
        wait
        tab2=`mysql -u${MYSQL_USER} -p${MYSQL_ROOT_PASSWORD} -P${MYSQL_PORT} -h${MYSQL_IP} -e "SELECT count(TABLE_NAME) FROM information_schema.TABLES WHERE TABLE_SCHEMA='gvnfm';"`
	tab3=`echo $tab2|awk '{print $2}'`
        if [ $tab3 -gt 0  ] ; then
        echo "TABLE CREATE SUCCESSFUL"
    fi
else
    echo "table already existed"
    exit 1
fi
 }

if [ ! -f /service/vfc/gvnfm/vnflcm/lcm/docker/db.txt ]; then
    echo 1 > /service/vfc/gvnfm/vnflcm/lcm/docker/db.txt
    echo `pwd` >> /service/vfc/gvnfm/vnflcm/lcm/docker/db.txt
    create_database
else
    echo "database already existed"
fi
