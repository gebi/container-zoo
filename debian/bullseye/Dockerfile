FROM debian:bullseye
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && echo 'APT::Install-Recommends "false";' >/etc/apt/apt.conf.d/10own \
    && echo 'Acquire::PDiffs "false";' >>/etc/apt/apt.conf.d/10own \
    && echo 'deb http://172.17.0.1:9999/debian bullseye main contrib non-free' >/etc/apt/sources.list \
    && echo 'deb http://172.17.0.1:9999/debian bullseye-updates main contrib non-free' >>/etc/apt/sources.list \
    && echo 'deb http://172.17.0.1:9999/debian-security bullseye-security main contrib non-free' >>/etc/apt/sources.list \
    && apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -q
