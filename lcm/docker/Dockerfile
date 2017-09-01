FROM ubuntu:14.04

ARG HTTP_PROXY=${HTTP_PROXY}
ARG HTTPS_PROXY=${HTTPS_PROXY}
ARG MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}

ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY
ENV MYSQL_ROOT_PASSWORD $MYSQL_ROOT_PASSWORD

RUN apt-get update && \
    apt-get install -y python-devel && \
    apt-get install -y python-virtualenv && \
    apt-get install -y python-setuptools && \
    apt-get install -y python-dev && \
    apt-get install -y python-pip && \
    apt-get install -y openssl-devel && \
    apt-get install -y mysql-devel && \
    apt-get install -y gcc && \
    apt-get install -y libffi-devel && \
    apt-get install -y redis && \
    apt-get install -y libmysqlclient-dev && \
    apt-get install -y redis-server && \
    apt-get install -y mysql-server && \
    apt-get install -y mysql-client && \
    apt-get install -y wget && \
    apt-get install -y unzip

ADD . /service
RUN cd /service

# get binary zip from nexus
RUN wget -q -O vfc-gvnfm-vnflcm-lcm.zip 'https://nexus.onap.org/service/local/artifact/maven/redirect?r=snapshots&g=org.onap.vfc.gvnfm.vnflcm&a=vfc-gvnfm-vnflcm-lcm&v=LATEST&e=zip' && \
    unzip vfc-gvnfm-vnflcm-lcm.zip && \
    rm -rf vfc-gvnfm-vnflcm-lcm.zip

# get db scripts from nexus
RUN wget -q -O vfc-gvnfm-vnfres-res.zip 'https://nexus.onap.org/service/local/artifact/maven/redirect?r=snapshots&g=org.onap.vfc.gvnfm.vnfres&a=vfc-gvnfm-vnfres-res&v=LATEST&e=zip' && \
    unzip vfc-gvnfm-vnfres-res.zip vfc/gvnfm/vnfres/res/assembly/*.* && \
    mv ./vfc/gvnfm/vnfres/res/assembly/bin ./bin && \
    mv ./vfc/gvnfm/vnfres/res/assembly/dbscripts ./dbscripts && \
    rm -rf vfc-gvnfm-vnfres-res.zip

EXPOSE 8801
EXPOSE 3306

WORKDIR /service/vfc/gvnfm/vnflcm/

CMD lcm/docker/instance_init.sh
