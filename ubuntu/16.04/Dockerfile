FROM ubuntu:xenial-20210416
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && echo 'APT::Install-Recommends "false";' >/etc/apt/apt.conf.d/10own \
    && echo 'Acquire::PDiffs "false";' >>/etc/apt/apt.conf.d/10own \
    && echo 'deb http://172.17.0.1:9999/ubuntu xenial main restricted universe multiverse' >/etc/apt/sources.list \
    && echo 'deb http://172.17.0.1:9999/ubuntu xenial-updates main restricted universe multiverse' >>/etc/apt/sources.list \
    && echo 'deb http://172.17.0.1:9999/ubuntu xenial-security main restricted universe multiverse' >>/etc/apt/sources.list \
    && apt-get update -q \
    && apt-get upgrade -y -q \
    && apt-get install -y -q --no-install-recommends vim-nox curl ca-certificates apt-transport-https build-essential devscripts equivs \
    && apt-get install -y -q software-properties-common \
    && apt-get clean
