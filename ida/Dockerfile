FROM local/ubuntu:xenial
MAINTAINER Michael Gebetsroither <mgebetsroither@mgit.at>

COPY sha1sums /

RUN set -ex \
    && curl -sS https://out7.hex-rays.com/files/idafree70_linux.run >idafree70_linux.run \
    && sha1sum -c sha1sums \
    && chmod 755 idafree70_linux.run \
    && ./idafree70_linux.run --mode unattended --prefix /opt/idafree-7.0 \
    && rm -f idafree70_linux.run \
    && apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q x11-common

RUN set -ex \
    && rm -f /opt/idafree-7.0/libX11-xcb.so.1 \
    && (echo -n "highly secure but dont tell" |hexdump -n 16 -v -e '/1 "%02x"'; echo )>/etc/machine-id \
    && apt-get update -q \
    && apt-get install -y -q libxext6 libxcb1 libx11-xcb1 libfontconfig1 libxi6 libsm6 xkb-data

#&& apt-get install -y -q libqt5gui5
