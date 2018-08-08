#!/bin/bash

CMD=$1

for i in potato woody sarge etch lenny squeeze; do
    if [[ $CMD == "build" ]]; then
        echo "Building: $i"
        docker build -t gebi/debian-vintage:$i $i/docker
        docker push gebi/debian-vintage:$i
    elif [[ $CMD == "test" ]]; then
        docker run -it --rm gebi/debian-vintage:$i /usr/bin/env cat /etc/debian_version
    fi
done
