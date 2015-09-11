#! /bin/bash

set -e
set -x

DISK_IMAGE=$(realpath ${1:-./overcloud-full.qcow2})
#PUPPET_REF=${2:-{{ puppet_neutron_ref }}}
PUPPET_ELEMENTS_REF=${3:-{{ puppet_elements_ref }}}

RPM_URLS=({{ rpms_for_image }})


echo "Updating image: $DISK_IMAGE"
#echo "Using Puppet Neutron ref: ${PUPPET_REF}"

mkdir -p /tmp/update-osp-image
cd /tmp/update-osp-image
cp $DISK_IMAGE .

# create tripleo-puppet-elements
if [ ! -d "tripleo-puppet-elements" ]; then
    git init tripleo-puppet-elements
fi

cd tripleo-puppet-elements
git fetch https://review.openstack.org/openstack/tripleo-puppet-elements ${PUPPET_ELEMENTS_REF} && git checkout FETCH_HEAD
cd ..


add_rpm_from_url () {
  rpm_url=$1
  file_name=${rpm_url##*/}
  curl -o "${file_name}" "${rpm_url}"
  virt-customize -a overcloud-full.qcow2 --upload ${file_name}:/tmp/${file_name}
  virt-customize -a overcloud-full.qcow2 --run-command "rpm -Uvh /tmp/${file_name}"
  virt-customize -a overcloud-full.qcow2 --run-command "rm /tmp/${file_name}"

}

# install virt-customize
# sudo yum install -y libguestfs-tools

# set password for development
virt-customize -a overcloud-full.qcow2 --root-password password:***REMOVED***

# now patch the image with RPMs
for rpm_url in ${RPM_URLS[*]}
do
  add_rpm_from_url "${rpm_url}"
done

# not sure if this is needed, but cleanup any SElinux problems caused by the image patching
virt-customize -a overcloud-full.qcow2 --run-command 'chcon -Rv --reference=/usr/lib/python2.7/site-packages/neutron /usr/lib/python2.7/site-packages/networking_cisco*'

# update 40-hiera-datafiles
virt-customize -a overcloud-full.qcow2 --upload tripleo-puppet-elements/elements/hiera/os-refresh-config/configure.d/40-hiera-datafiles:/usr/libexec/os-refresh-config/configure.d

mv overcloud-full.qcow2 "${DISK_IMAGE}"
