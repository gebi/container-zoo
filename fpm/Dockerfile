FROM local/debian:stable-dev
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

# /.cpanm is for cpanminus to work as un-named user
RUN set -ex \
    && apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q ruby ruby-dev rubygems cpanminus \
    && gem install --no-ri --no-rdoc fpm \
    && install -d -m 777 /.cpanm
