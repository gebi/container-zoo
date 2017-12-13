FROM debian:jessie
MAINTAINER Michael Gebetsroither <mgebetsroither@mgit.at>

RUN set -ex \
    && echo 'APT::Install-Recommends "false";' >/etc/apt/apt.conf.d/10own \
    && echo 'Acquire::PDiffs "false";' >>/etc/apt/apt.conf.d/10own \
    && echo 'deb http://172.17.0.1:9999/debian jessie main contrib non-free' >/etc/apt/sources.list \
    && echo 'deb http://172.17.0.1:9999/debian jessie-updates main' >>/etc/apt/sources.list \
    && echo 'deb http://172.17.0.1:9999/debian-security jessie/updates main' >>/etc/apt/sources.list \
    && apt-get update -q \
    && apt-get upgrade -y -q \
    && apt-get install -y -q --no-install-recommends vim-nox ca-certificates build-essential devscripts equivs \
    && apt-get clean
