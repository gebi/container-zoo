FROM debian:wheezy
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && echo 'APT::Install-Recommends "false";' >/etc/apt/apt.conf.d/10own \
    && echo 'Acquire::PDiffs "false";' >>/etc/apt/apt.conf.d/10own \
    && echo 'deb http://172.17.0.1:9999/debian wheezy main contrib non-free' >/etc/apt/sources.list \
    && echo 'deb http://172.17.0.1:9999/debian wheezy-updates main' >>/etc/apt/sources.list \
    && echo 'deb http://172.17.0.1:9999/debian-security wheezy/updates main' >>/etc/apt/sources.list
    && apt-get update -q \
    && apt-get upgrade -y -q

RUN set -ex \
    && apt-get install -y -q --no-install-recommends apt-file \
    && apt-file update

RUN set -ex \
    && apt-get install -y -q --no-install-recommends vim-nox curl ca-certificates apt-transport-https build-essential devscripts equivs
