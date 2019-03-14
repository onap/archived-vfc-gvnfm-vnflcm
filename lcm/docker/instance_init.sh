#!/bin/bash
# echo "No service needs init."
MYSQL_ROOT_PASSWORD=$0
MYSQL_PORT=$1
MYSQL_IP=$2

function create_database {
#    cd /service/vfc/nfvo/lcm/resources/bin
    cd /service/vfc/nfvo/db/resources/vnflcm/bin
   bash initDB.sh root $MYSQL_ROOT_PASSWORD $MYSQL_PORT $MYSQL_IP
#    bash initDB.sh root $MYSQL_ROOT_PASSWORD 3306 127.0.0.1
    cd /service
 }

create_database