#! /bin/bash

set -e
set -x

DISK_IMAGE=$(realpath ${1:-./overcloud-full.qcow2})
PUPPET_REF=${2:-{{ puppet_neutron_ref }}}

CISCO_RPM_URL=${3:-{{ networking_cisco_rpm_url }}}

echo "Updating image: $DISK_IMAGE"
echo "Using Puppet Neutron ref: ${PUPPET_REF}"

mkdir -p /tmp/update-osp-image
cd /tmp/update-osp-image
cp $DISK_IMAGE .


# get current puppet-neturon
if [ ! -d "puppet-neutron" ]; then
    git clone https://review.openstack.org/openstack/puppet-neutron
fi

cd puppet-neutron
git fetch https://review.openstack.org/openstack/puppet-neutron ${PUPPET_REF}  && git checkout FETCH_HEAD
cd ..


# install virt-customize
# sudo yum install -y libguestfs-tools

curl -o python-networking-cisco.noarch.rpm "${CISCO_RPM_URL}"

virt-customize -a overcloud-full.qcow2 --root-password password:***REMOVED***
virt-customize -a overcloud-full.qcow2 --upload python-networking-cisco.noarch.rpm:/tmp/
virt-customize -a overcloud-full.qcow2 --run-command 'rpm -Uvh /tmp/python-networking-cisco.noarch.rpm'
virt-customize -a overcloud-full.qcow2 --run-command 'rm /tmp/python-networking-cisco.noarch.rpm'
virt-customize -a overcloud-full.qcow2 --run-command 'chcon -Rv --reference=/usr/lib/python2.7/site-packages/neutron /usr/lib/python2.7/site-packages/networking_cisco*'
virt-copy-in -a overcloud-full.qcow2 puppet-neutron/* /usr/share/openstack-puppet/modules/neutron
virt-customize -a overcloud-full.qcow2 --run-command 'chcon -Rv --reference=/usr/share/openstack-puppet/modules/nova /usr/share/openstack-puppet/modules/neutron'
virt-customize -a overcloud-full.qcow2 --run-command 'crudini --del /usr/lib/python2.7/site-packages/networking_cisco-*.egg-info/entry_points.txt  neutron.core_plugins'
virt-customize -a overcloud-full.qcow2 --run-command 'crudini --del /usr/lib/python2.7/site-packages/networking_cisco-*.egg-info/entry_points.txt  neutron.ml2.mechanism_drivers ncs'
virt-customize -a overcloud-full.qcow2 --run-command 'crudini --del /usr/lib/python2.7/site-packages/networking_cisco-*.egg-info/entry_points.txt  neutron.ml2.mechanism_drivers cisco_ncs'
virt-customize -a overcloud-full.qcow2 --run-command 'crudini --del /usr/lib/python2.7/site-packages/networking_cisco-*.egg-info/entry_points.txt  neutron.ml2.mechanism_drivers cisco_nexus'

mv overcloud-full.qcow2 "${DISK_IMAGE}"