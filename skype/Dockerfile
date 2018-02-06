# Usage:
#   docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/.config/skypeforlinux:/mnt/.config/skypeforlinux -e HOME=/mnt --user 1000:1000 local/skype

FROM local/ubuntu:16.04
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \
    && curl -sSf https://repo.skype.com/data/SKYPE-GPG-KEY | apt-key add - \
    && echo "deb [arch=amd64] https://repo.skype.com/deb stable main" >/etc/apt/sources.list.d/skype.list \
    && apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get -y -q --no-install-recommends install skypeforlinux

# fixups for skype to run
RUN set -ex \
    && (echo -n "skype highly secure but dont tell" |md5sum |cut -d\  -f1)>/etc/machine-id

#ENTRYPOINT ["skypeforlinux"]
