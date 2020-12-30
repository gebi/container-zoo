###
## BUILD image
###

FROM ubuntu:20.04 AS build-image
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y ca-certificates git golang gcc libc-dev libaom-dev

RUN mkdir -p /go/src/github.com/Kagami \
  && cd /go/src/github.com/Kagami \
  && git clone https://github.com/Kagami/go-avif.git \
  && GOPATH=/go go get -v ./...


###
## RUNTIME image
###

FROM ubuntu:20.04 AS runtime-image
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y libaom0

COPY --from=build-image /go/bin/avif /avif

ENTRYPOINT ["/avif"]

