FROM debian:buster
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && echo 'APT::Install-Recommends "false";' >/etc/apt/apt.conf.d/10own \
    && echo 'Acquire::PDiffs "false";' >>/etc/apt/apt.conf.d/10own \
    && echo 'deb http://172.17.0.1:9999/debian buster main contrib non-free' >/etc/apt/sources.list \
    && echo 'deb http://172.17.0.1:9999/debian buster-updates main' >>/etc/apt/sources.list \
    && echo 'deb http://172.17.0.1:9999/debian-security buster/updates main' >>/etc/apt/sources.list
    && apt-get update -q \
    && apt-get upgrade -y -q
