#!/bin/bash

set -ex

parallel docker pull -- alpine:latest debian:jessie debian:stretch ubuntu:xenial

# base images
docker build $* -t local/alpine-dev alpine-dev
docker build $* -t local/debian:stretch debian/stretch
docker build $* -t local/debian:jessie debian/jessie
docker build $* -t local/ubuntu:16.04 ubuntu/16.04

# not used anymore
#docker build $* -t local/scribus scribus
