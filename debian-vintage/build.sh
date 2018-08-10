#!/bin/bash

set -e

CMD=$1

ret=0
REL="potato woody sarge etch lenny squeeze"
DOCKER_OPTS_="${DOCKER_OPTS:-}"

build () {
    local i="$1"
    echo "Building: $i"
    (
        docker build $DOCKER_OPTS_ -t gebi/debian-vintage:$i $i/docker
    ) 2>&1 |tee $i.log
}

build-dev() {
    local i="$1"
    echo "Building DEV: $i"
    mkdir -p $i-dev
    case "$i" in
        potato) apt_opts="" ;;
        default) apt_opts="--no-install-recommends" ;;
    esac
    if [[ $i == "etch" ]]; then
        apt_opts="$apt_opts --force-yes"
    fi
    cat >$i-dev/Dockerfile <<EOT
FROM gebi/debian-vintage:$i
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN set -ex \\
    && /bin/echo -e 'APT::Install-Recommends "false";\nAPT::Install-Suggests "false";' >/etc/apt/apt.conf \\
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -q $apt_opts build-essential \\
    && rm /etc/apt/apt.conf && touch /etc/apt/apt.conf
EOT
    (
        docker build $DOCKER_OPTS_ -t gebi/debian-vintage:$i-dev $i-dev/
    )  2>&1 |tee $i-dev.log
}


if [[ $CMD == "build" || $CMD == "build-dev" ]]; then
    if [[ $2 != "" ]]; then
        "$1" "$2"
    else
        parallel $0 $1 -- $REL
    fi
elif [[ $CMD == "push" ]]; then
    to_push=""
    for i in $REL; do
        to_push="$to_push gebi/debian-vintage:$i gebi/debian-vintage:$i-dev"
    done
    parallel docker push -- $to_push
elif [[ $CMD == "test" ]]; then
    for i in $REL; do
        echo -en "$i:\t"
        docker run -it --rm gebi/debian-vintage:$i /usr/bin/env cat /etc/debian_version
        echo -en "$i-dev:\t"
        docker run -it --rm gebi/debian-vintage:$i-dev /usr/bin/env cat /etc/debian_version
        rettmp=$?
        if [[ $rettmp != 0 ]]; then
            ret=1
        fi
    done
fi

exit $ret
