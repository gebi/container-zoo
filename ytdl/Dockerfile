FROM local/ubuntu:18.04
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q youtube-dl python3-pip ffmpeg \
    && pip3 install --upgrade youtube-dl
