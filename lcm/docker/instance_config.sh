#!/bin/bash

MSB_IP=`echo $MSB_ADDR | cut -d: -f 1`
MSB_PORT=`echo $MSB_ADDR | cut -d: -f 2`

if [ $MSB_IP ]; then
    sed -i "s|MSB_SERVICE_IP.*|MSB_SERVICE_IP = '$MSB_IP'|" vfc/gvnfm/vnflcm/lcm/lcm/pub/config/config.py
fi

if [ $MSB_PORT ]; then
    sed -i "s|MSB_SERVICE_PORT.*|MSB_SERVICE_PORT = '$MSB_PORT'|" vfc/gvnfm/vnflcm/lcm/lcm/pub/config/config.py
fi

if [ $SERVICE_IP ]; then
    sed -i "s|\"ip\": \".*\"|\"ip\": \"$SERVICE_IP\"|" vfc/gvnfm/vnflcm/lcm/lcm/pub/config/config.py
fi

sed -i "s/127.0.0.1:80/$MSB_IP:$MSB_PORT/" vfc/gvnfm/vnflcm/lcm/lcm/pub/config/config.py

# Configure MYSQL
MYSQL_IP=`echo $MYSQL_ADDR | cut -d: -f 1`
MYSQL_PORT=`echo $MYSQL_ADDR | cut -d: -f 2`
echo "MYSQL_ADDR=$MYSQL_ADDR"

sed -i "s|DB_IP.*|DB_IP = '$MYSQL_IP'|" vfc/gvnfm/vnflcm/lcm/lcm/pub/config/config.py
sed -i "s|DB_PORT.*|DB_PORT = $MYSQL_PORT|" vfc/gvnfm/vnflcm/lcm/lcm/pub/config/config.py
sed -i "s|REDIS_HOST.*|REDIS_HOST = '$MYSQL_IP'|" vfc/gvnfm/vnflcm/lcm/lcm/pub/config/config.py

cat vfc/gvnfm/vnflcm/lcm/lcm/pub/config/config.py
