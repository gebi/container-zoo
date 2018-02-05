FROM local/ubuntu:16.04
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

COPY sha1sums /

# download
RUN set -ex \
    #&& curl -sSf http://172.17.0.1/PUBLIC/ida/idafree70_linux.run >idafree70_linux.run \
    #    || curl -sS https://out7.hex-rays.com/files/idafree70_linux.run >idafree70_linux.run \
    && curl -sS https://out7.hex-rays.com/files/idafree70_linux.run >idafree70_linux.run \
    && sha1sum -c sha1sums \
    && chmod 755 idafree70_linux.run

# install
RUN set -ex \
    && ./idafree70_linux.run --mode unattended --prefix /opt/idafree


###
## final image
###

FROM local/ubuntu:16.04
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

# install dependencies
RUN set -ex \
    && apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends x11-common libxext6 libxcb1 libx11-xcb1 libfontconfig1 libxi6 libsm6 xkb-data

COPY --from=0 /opt/idafree /opt/idafree

# fixups
#   libX11-xcb.so.1 from ida installer is 32bit
#   ida prints an error about missing machine id
RUN set -ex \
    && rm -f /opt/idafree/libX11-xcb.so.1 \
    && (echo -n "highly secure but dont tell" |hexdump -n 16 -v -e '/1 "%02x"'; echo )>/etc/machine-id
