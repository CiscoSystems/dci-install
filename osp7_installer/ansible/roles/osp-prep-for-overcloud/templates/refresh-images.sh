#! /bin/bash

set -e
set -x

glance image-delete bm-deploy-kernel bm-deploy-ramdisk overcloud-full overcloud-full-initrd overcloud-full-vmlinuz

cd /home/stack/images
rm overcloud-full.qcow2
tar -xf overcloud-full.tar

rm -rf /tmp/update-osp-image
/home/stack/bin/build-disk-image.sh "$@"

openstack overcloud image upload

