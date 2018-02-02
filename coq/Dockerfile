FROM local/ubuntu:18.04
MAINTAINER Michael Gebetsroither <mgebetsroither@mgit.at>

RUN set -ex \
    && add-apt-repository ppa:jgross-h/coq-8.7-daily \
    && apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q coq coqide
