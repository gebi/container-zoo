#!/bin/bash

set -ex

docker build $* -t local/alpine-dev alpine-dev
docker build $* -t local/debian:stretch debian/stretch
