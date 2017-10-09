#!/bin/bash
cd /service/vfc/gvnfm/vnflcm/lcm
./run.sh

while [ ! -f logs/runtime_lcm.log ]; do
    sleep 1
done
tail -F logs/runtime_lcm.log
