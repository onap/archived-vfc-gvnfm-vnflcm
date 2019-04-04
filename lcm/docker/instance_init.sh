#!/bin/bash

MYSQL_IP=`echo $MYSQL_ADDR | cut -d: -f 1`
MYSQL_PORT=`echo $MYSQL_ADDR | cut -d: -f 2`

if [ $MYSQL_AUTH ]; then
    MYSQL_ROOT_USER=`echo $MYSQL_AUTH | cut -d: -f 1`
    MYSQL_ROOT_PASSWORD=`echo $MYSQL_AUTH | cut -d: -f 2`
else
    MYSQL_ROOT_USER="root"
    MYSQL_ROOT_PASSWORD="root"
fi

function create_database {
    cd /service/vfc/gvnfm/vnflcm/lcm/resources/bin
    bash initDB.sh $MYSQL_ROOT_USER $MYSQL_ROOT_PASSWORD $MYSQL_PORT $MYSQL_IP
}

function migrate_database {
    cd /service/vfc/gvnfm/vnflcm/lcm
    python manage.py makemigrations database
    python manage.py migrate --fake
    python manage.py migrate
}

GET_VNFM_DB="show databases like 'gvnfm';"
VNFM_DB=`mysql -u$MYSQL_ROOT_USER -p$MYSQL_ROOT_PASSWORD -P$MYSQL_PORT -h$MYSQL_IP -e "$GET_VNFM_DB"`
if [[ "$VNFM_DB" == "" ]]; then
    create_database
    migrate_database
fi
