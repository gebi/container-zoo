#!/bin/bash

set -ex

parallel docker pull -- alpine:latest debian:jessie debian:stretch ubuntu:xenial ubuntu:bionic

# base images
docker build $* -t local/alpine-dev alpine-dev
docker build $* -t local/debian:stretch debian/stretch
docker build $* -t local/debian:jessie debian/jessie

docker build $* -t local/ubuntu:16.04 ubuntu/16.04
docker tag local/ubuntu:16.04 local/ubuntu:xenial

docker build $* -t local/ubuntu:18.04 ubuntu/18.04
docker tag local/ubuntu:18.04 local/ubuntu:bionic

# app images
docker build -t local/hledger hledger
docker build -t local/ida ida

# not used anymore
#docker build $* -t local/scribus scribus
#docker build $* -t local/coq coq
