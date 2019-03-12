FROM local/fpm
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q request-tracker4

RUN set -ex \
    && apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q libmodule-install-perl libnet-oauth2-perl
