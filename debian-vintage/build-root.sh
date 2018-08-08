#!/bin/bash

build() {
    local rel="$1"
    local workdir="$2"
    local arch="i386"
    local opts=""

    local rootfs=$workdir/rootfs
    local dockerfs=$workdir/docker

    if [[ $rel == "etch" ]]; then
        opts="--no-check-gpg"
    fi
    debootstrap $opts --arch=$arch $rel $rootfs http://archive.debian.org/debian/

    rm -rf $rootfs/{dev,proc}
    mkdir -p $rootfs/{dev,proc}

    #mkdir -p $rootfs/etc
    #cp /etc/resolv.conf $rootfs/etc/

    mkdir $dockerfs
    tar --numeric-owner -caf $dockerfs/rootfs.tar.xz -C $rootfs --transform='s,^./,,' .

    cat >$dockerfs/Dockerfile <<EOT
FROM scratch
MAINTAINER Michael Gebetsroither <michael@mgeb.org>

ADD rootfs.tar.xz /
CMD ["/bin/bash"]
EOT
}

for i in potato woody sarge etch lenny squeeze; do
    if [ -d $i ]; then
        echo "$i already exists... skipping"
        continue
    fi
    echo "Building: $i"
    (
        mkdir $i
        build $i $i |tee $i/build.log
    )
done
