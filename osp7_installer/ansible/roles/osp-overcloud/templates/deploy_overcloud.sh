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
  --neutron-flat-networks {{ neutron_flat_networks }} \
  --neutron-public-interface {{ controller_external_nic }} \
{% if osp_version == 7 %}
  --hypervisor-neutron-public-interface {{ compute_tenant_nic }} \
{% endif %}
  --neutron-physical-bridge {{ neutron_tenant_bridge }} \
{% if network_isolation %}
  -e /usr/share/openstack-tripleo-heat-templates/environments/network-isolation.yaml \
{% else %}
    -e /usr/share/openstack-tripleo-heat-templates/overcloud-resource-registry-puppet.yaml \
{% endif %}
  -e /home/stack/templates/networking-cisco-environment.yaml \
{% if nfs_for_storage %}
  -e /home/stack/templates/nfs-environment.yaml \
{% endif %}
{% if deploy_with_flavors %}
  {{ deploy_with_flavors_args }} \
{% endif %}
  --neutron-tunnel-type vlan \
{% if neutron_external_bridge == neutron_tenant_bridge %}
  --neutron-bridge-mappings datacentre:{{ neutron_tenant_bridge }} \
{% else %}
  --neutron-bridge-mappings "datacentre:{{ neutron_tenant_bridge }},external:{{ neutron_external_bridge }}" \
{% endif %}
  --neutron-network-vlan-ranges {{ network_nexus_vlan_range }} \
{% if deploy_extra_args %}
   {{ deploy_extra_args }} \
{% endif %}
  --ntp-server 1.ntp.esl.cisco.com

