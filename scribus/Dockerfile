FROM local/ubuntu:16.04
#FROM local/debian:stretch

ENV DISPLAY :0

ADD run.sh /

RUN set -ex \
    && add-apt-repository ppa:scribus/ppa \
    && apt-get update \
    && apt-get install -qy scribus-ng fonts-dejavu fonts-liberation hyphen-de xfonts-scalable gsfonts-x11 icc-profiles-free scribus-template \
    && useradd -m -s /bin/bash gebi

RUN set -ex \
    && chmod 755 /run.sh \
    && apt-get install -qy poppler-utils fonts-arkpandora
    #&& apt-get install -qy poppler-utils ttf-mscorefonts-installer

CMD /run.sh
