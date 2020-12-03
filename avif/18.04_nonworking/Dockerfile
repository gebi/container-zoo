# currently does not build (some gpg error on apt install)
FROM ubuntu:18.04

RUN apt-get update \
  && echo 'APT::Install-Recommends "false";' >/etc/apt/apt.conf.d/10own \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common \
  && add-apt-repository -y ppa:jonathonf/ffmpeg-4 \
  && apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y git golang libc-dev libaom-dev

RUN mkdir -p /go/src/github.com/Kagami \
  && cd /go/src/github.com/Kagami \
  && git clone https://github.com/Kagami/go-avif.git \
  && GOPATH=/go go get -v ./...

ENTRYPOINT ["/go/bin/avif"]
