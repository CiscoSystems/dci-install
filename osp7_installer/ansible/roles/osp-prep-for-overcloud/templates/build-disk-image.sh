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
  virt-customize --selinux-relabel -a overcloud-full.qcow2 --run-command "rpm -Uvh /tmp/${file_name}"
  virt-customize -a overcloud-full.qcow2 --run-command "rm /tmp/${file_name}"

}

correct_selinux_context () {
    ref_dir=$1
    target_dir=$2
    virt-customize -a overcloud-full.qcow2 --run-command "chcon -Rv --reference=${ref_dir} ${target_dir}"
}

# install virt-customize
# sudo yum install -y libguestfs-tools

# set password for development
virt-customize -a overcloud-full.qcow2 --root-password password:cisco123
virt-customize --selinux-relabel -a overcloud-full.qcow2 --run-command "sed -i 's/.*PasswordAuthentication.*/PasswordAuthentication yes/g' /etc/ssh/sshd_config"
virt-customize --selinux-relabel -a overcloud-full.qcow2 --run-command "sed -i 's/PasswordAuthentication.*/PasswordAuthentication yes/g' /etc/ssh/sshd_config"

# now patch the image with RPMs
for rpm_url in ${RPM_URLS[*]}
do
  add_rpm_from_url "${rpm_url}"
done

## first udpate all the openstack RPMs
#virt-customize -a overcloud-full.qcow2 --run-command 'subscription-manager register --user={{ rhel_username }} --password={{ rhel_password }}'
#virt-customize -a overcloud-full.qcow2 --run-command 'subscription-manager attach --pool={{ rhel_pool }}'
#virt-customize -a overcloud-full.qcow2 --run-command 'subscription-manager repos --disable=*'
#virt-customize -a overcloud-full.qcow2 --run-command 'subscription-manager repos --enable=rhel-7-server-openstack-7.0-rpms'
#virt-customize -a overcloud-full.qcow2 --run-command 'yum makecache'
#virt-customize -a overcloud-full.qcow2 --run-command 'yum update -y'
#virt-customize -a overcloud-full.qcow2 --run-command 'yum clean all'


# correct SELinux security context
correct_selinux_context '/usr/lib/python2.7/site-packages/neutron' '/usr/lib/python2.7/site-packages/networking_cisco*'
correct_selinux_context '/usr/lib/python2.7/site-packages/neutron' '/usr/lib64/python2.7/site-packages/lxml*'
correct_selinux_context '/usr/lib/python2.7/site-packages/neutron' '/usr/lib/python2.7/site-packages/UcsSdk*'
correct_selinux_context '/usr/lib/python2.7/site-packages/neutron' '/usr/share/openstack-puppet'

# update 40-hiera-datafiles
virt-customize --selinux-relabel -a overcloud-full.qcow2 --upload tripleo-puppet-elements/elements/hiera/os-refresh-config/configure.d/40-hiera-datafiles:/usr/libexec/os-refresh-config/configure.d

mv overcloud-full.qcow2 "${DISK_IMAGE}"
