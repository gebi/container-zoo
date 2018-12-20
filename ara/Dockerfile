FROM local/debian:stretch
LABEL maintainer="Michael Gebetsroither <michael@mgeb.org>"

RUN set -ex \
    && apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends gcc python-pip python-setuptools python-dev libffi-dev libssl-dev \
    && pip install --upgrade pip

RUN set -ex \
    && pip install ara

CMD ara-manage runserver -h 0.0.0.0
