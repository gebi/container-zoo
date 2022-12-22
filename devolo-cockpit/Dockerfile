# container to execute devolo-cockpit on modern linux systems properly
# Usage: WARNING: running as root
#   docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --network=host local/devolo-cockpit
# (c) 2022 Michael Gebetsroither <m.gebetsr@gmail.com>

FROM local/debian:bullseye
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

ARG DEVOLO_COCKPIT_VERSION="devolo-cockpit-v5-2-0-185-linux.run"

# prep container
RUN set -ex \
    && dpkg --add-architecture i386 \
    && apt-get update -q\
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends curl ca-certificates

COPY sha256sums /

# download & install
RUN set -ex \
    && curl -sS https://www.devolo.de/fileadmin/Web-Content/DE/products/hnw/devolo-cockpit/software/${DEVOLO_COCKPIT_VERSION} >${DEVOLO_COCKPIT_VERSION} \
    && sha256sum -c sha256sums \
    && chmod 755 ${DEVOLO_COCKPIT_VERSION} \
    && DEBIAN_FRONTEND=noninteractive ./${DEVOLO_COCKPIT_VERSION} -y -q --no-install-recommends

COPY start.sh /

# fixups
RUN set -ex \
    && chmod 755 start.sh \
    && (echo -n "devolo highly secure but dont tell" |md5sum |cut -d\  -f1)>/etc/machine-id

ENTRYPOINT ["/start.sh"]
