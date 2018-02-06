# Usage:
#   docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/.config/Signal:/mnt/.config/Signal --user 1000:1000 -e HOME=/mnt local/signal

FROM local/ubuntu:16.04
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && curl -sSf https://updates.signal.org/desktop/apt/keys.asc | apt-key add - \
    && echo "deb [arch=amd64] https://updates.signal.org/desktop/apt xenial main" >>/etc/apt/sources.list.d/signal-xenial.list \
    && apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends signal-desktop libx11-xcb1

ENTRYPOINT ["signal-desktop"]
