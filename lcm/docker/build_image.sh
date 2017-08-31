#!/bin/bash

MYSQL_ROOT_PASSWORD="root"
PROXY_ARGS=""
ORG="onap"
VERSION="1.0.0-SNAPSHOT"
IMAGE="vfc-gvnfm-vnflcm"
DOCKER_REPOSITORY="nexus3.onap.org:10003"

if [ $HTTP_PROXY ]; then
    PROXY_ARGS+="--build-arg HTTP_PROXY=${HTTP_PROXY}"
fi
if [ $HTTPS_PROXY ]; then
    PROXY_ARGS+=" --build-arg HTTPS_PROXY=${HTTPS_PROXY}"
fi

function build_vnflcm {
    docker build ${PROXY_ARGS} --build-arg MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} -t ${ORG}/${IMAGE}:${VERSION} -t ${ORG}/${IMAGE}:latest .
}

function push_vnflcm {
    docker push ${DOCKER_REPOSITORY}/${ORG}/${IMAGE}:${VERSION}
    docker push ${DOCKER_REPOSITORY}/${ORG}/${IMAGE}:latest
}

build_vnflcm
push_vnflcm
docker image list
