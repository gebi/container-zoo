FROM local/centos:7
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && yum install -y cpanspec rpm-build

COPY rpmmacros /root/.rpmmacros
