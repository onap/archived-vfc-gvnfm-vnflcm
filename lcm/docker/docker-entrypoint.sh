#!/bin/bash

if [ -z "$SERVICE_IP" ]; then
    export SERVICE_IP=`hostname -i`
fi
echo "SERVICE_IP=$SERVICE_IP"

# Configure service based on docker environment variables
python vfc/gvnfm/vnflcm/lcm/lcm/pub/config/config.py
cat vfc/gvnfm/vnflcm/lcm/lcm/pub/config/config.py

# microservice-specific one-time initialization
vfc/gvnfm/vnflcm/lcm/docker/instance_init.sh

date > init.log

# Start the microservice
vfc/gvnfm/vnflcm/lcm/docker/instance_run.sh
