FROM ubuntu:14.04

ARG HTTP_PROXY=${HTTP_PROXY}
ARG HTTPS_PROXY=${HTTPS_PROXY}

ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY

RUN echo "mysql-server mysql-server/root_password password root" | debconf-set-selections
RUN echo "mysql-server mysql-server/root_password_again password root" | debconf-set-selections

RUN apt-get update && \
    apt-get install -y python-virtualenv && \
    apt-get install -y python-setuptools && \
    apt-get install -y python-dev && \
    apt-get install -y python-pip && \
    apt-get install -y gcc && \
    apt-get install -y libmysqlclient-dev && \
    apt-get install -y redis-server && \
    apt-get install -y mysql-server && \
    apt-get install -y mysql-client && \
    apt-get install -y wget && \
    apt-get install -y unzip && \
    apt-get install -y curl && \
    apt-get install -y build-essential && \
    apt-get install -y libssl-dev && \
    apt-get install -y libffi-dev

ADD . /service
WORKDIR /service

# get binary zip from nexus
RUN wget -q -O vfc-gvnfm-vnflcm-lcm.zip 'https://nexus.onap.org/service/local/artifact/maven/redirect?r=snapshots&g=org.onap.vfc.gvnfm.vnflcm.lcm&a=vfc-gvnfm-vnflcm-lcm&v=LATEST&e=zip' && \
    unzip vfc-gvnfm-vnflcm-lcm.zip && \
    rm -rf vfc-gvnfm-vnflcm-lcm.zip

# get db scripts from nexus
RUN wget -q -O vfc-gvnfm-vnfres-res.zip 'https://nexus.onap.org/service/local/artifact/maven/redirect?r=snapshots&g=org.onap.vfc.gvnfm.vnfres.res&a=vfc-gvnfm-vnfres-res&v=LATEST&e=zip' && \
    unzip vfc-gvnfm-vnfres-res.zip vfc/gvnfm/vnfres/res/assembly/*.* && \
    mv ./vfc/gvnfm/vnfres/res/assembly/bin ./bin && \
    mv ./vfc/gvnfm/vnfres/res/assembly/dbscripts ./dbscripts && \
    rm -rf vfc-gvnfm-vnfres-res.zip

RUN sed -i "s|bind-address.*|# bind-address = 127.0.0.1|" /etc/mysql/my.cnf

WORKDIR /service/vfc/gvnfm/vnflcm/lcm
RUN pip install -r requirements.txt

EXPOSE 8801
EXPOSE 3306
EXPOSE 6379

WORKDIR /service
ENTRYPOINT vfc/gvnfm/vnflcm/lcm/docker/docker-entrypoint.sh
