#! /bin/bash

source /home/stack/stackrc

cd /home/stack/

openstack overcloud deploy --templates \
  --control-scale {{ overcloud_control_scale }} \
  --compute-scale {{ overcloud_compute_scale }} \
  --ceph-storage-scale {{ overcloud_ceph_storage_scale }} \
  --block-storage-scale {{ overcloud_block_storage_scale }} \
  --swift-storage-scale {{ overcloud_swift_storage_scale }} \
  --neutron-network-type vlan \
  --neutron-disable-tunneling \
  --neutron-public-interface {{ neutron_public_nic }} \
  --hypervisor-neutron-public-interface {{ hypervisor_neutron_public_nic }} \
  -e /usr/share/openstack-tripleo-heat-templates/overcloud-resource-registry-puppet.yaml \
  -e /home/stack/templates/networking-cisco-environment.yaml \
{% if nfs_for_storage %}
  -e /home/stack/templates/nfs-environment.yaml \
{% endif %}
{% if deploy_with_flavors %}
  {{ deploy_with_flavors_args }} \
{% endif %}
  --neutron-tunnel-type vlan \
  --neutron-network-vlan-ranges {{ network_nexus_vlan_range }} \
{% if deploy_extra_args %}
   {{ deploy_extra_args }} \
{% endif %}
  --ntp-server 1.ntp.esl.cisco.com

