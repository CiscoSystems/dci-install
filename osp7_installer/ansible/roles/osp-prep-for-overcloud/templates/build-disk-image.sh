#! /bin/bash

set -e
set -x

DISK_IMAGE=$(realpath ${1:-./overcloud-full.qcow2})
PUPPET_REF=${2:-{{ puppet_neutron_ref }}}
PUPPET_ELEMENTS_REF=${3:-{{ puppet_elements_ref }}}
NET_CISCO_RPM_URL=${4:-{{ networking_cisco_rpm_url }}}
UCS_SDK_RPM_URL=${5:-{{ ucs_sdk_rpm_url }}}

RPM_URLS=({{ rpms_for_image }})


echo "Updating image: $DISK_IMAGE"
#echo "Using Puppet Neutron ref: ${PUPPET_REF}"

mkdir -p /tmp/update-osp-image
cd /tmp/update-osp-image
cp $DISK_IMAGE .

#
## get current puppet-neturon
#if [ ! -d "puppet-neutron" ]; then
#    git init puppet-neutron
#fi
#
#cd puppet-neutron
#git fetch https://review.openstack.org/openstack/puppet-neutron ${PUPPET_REF}  && git checkout FETCH_HEAD
#cd ..

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

#curl -o python-UcsSdk.noarch.rpm "${UCS_SDK_RPM_URL}"
#curl -o python-networking-cisco.noarch.rpm "${NET_CISCO_RPM_URL}"

# set password for development
virt-customize -a overcloud-full.qcow2 --root-password password:***REMOVED***

# install python-UcsSdk
#virt-customize -a overcloud-full.qcow2 --upload python-UcsSdk.noarch.rpm:/tmp/
#virt-customize -a overcloud-full.qcow2 --run-command 'rpm -Uvh /tmp/python-UcsSdk.noarch.rpm'
#virt-customize -a overcloud-full.qcow2 --run-command 'rm /tmp/python-UcsSdk.noarch.rpm'
#add_rpm_from_url "http://memory.cisco.com/osp7/rpms/rh/python-UcsSdk-0.8.2.5-1.el7ost.noarch.rpm"
#good

# install python-networking-cisco
#virt-customize -a overcloud-full.qcow2 --upload python-networking-cisco.noarch.rpm:/tmp/
#virt-customize -a overcloud-full.qcow2 --run-command 'rpm -Uvh /tmp/python-networking-cisco.noarch.rpm'
#virt-customize -a overcloud-full.qcow2 --run-command 'rm /tmp/python-networking-cisco.noarch.rpm'
#add_rpm_from_url "http://memory.cisco.com/osp7/rpms/rh/python-networking-cisco-2015.1.0-2.el7ost.noarch.rpm"
#good

#lxml
#add_rpm_from_url "http://memory.cisco.com/osp7/rpms/rh/python-lxml-3.2.1-5.el7_1.x86_64.rpm"
# good ?

# update neutron-puppet
#virt-copy-in -a overcloud-full.qcow2 puppet-neutron/* /usr/share/openstack-puppet/modules/neutron
#virt-customize -a overcloud-full.qcow2 --run-command 'chcon -Rv --reference=/usr/share/openstack-puppet/modules/nova /usr/share/openstack-puppet/modules/neutron'
#add_rpm_from_url "http://memory.cisco.com/osp7/rpms/rh/openstack-puppet-modules-2015.1.8-14.el7ost.noarch.rpm"

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
