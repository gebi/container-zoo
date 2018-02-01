FROM local/debian:stretch
MAINTAINER Michael Gebetsroither <mgebetsroither@mgit.at>

RUN set -ex \
    && apt-get update -q \
    && apt-get install -y -q hledger hledger-ui hledger-web python3-yaml python3-requests python3-dateutil \
    && apt-get clean
