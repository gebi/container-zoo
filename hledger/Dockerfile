FROM local/debian:buster
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

# WARNING: hledger REALLY requires the locale stuff, otherwise it will abort with:
#   hledger-web: /mnt/hledger-journal: hGetContents: invalid argument (invalid byte sequence)

RUN set -ex \
    && apt-get update -q \
    && apt-get install -y -q hledger hledger-ui hledger-web locales \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && apt-get clean
