FROM local/debian:stretch
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends apt-file \
    && apt-file update

RUN set -ex \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends vim-nox curl ca-certificates apt-transport-https build-essential devscripts equivs
