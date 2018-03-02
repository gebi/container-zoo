FROM local/debian:jessie
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && apt-get install -y -q --no-install-recommends apt-file \
    && apt-file update

RUN set -ex \
    && apt-get install -y -q --no-install-recommends vim-nox curl ca-certificates apt-transport-https build-essential devscripts equivs
