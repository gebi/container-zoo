FROM local/hledger
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && apt-get update -q \
    && apt-get install -y -q python3-yaml python3-requests python3-dateutil make \
    && apt-get clean
