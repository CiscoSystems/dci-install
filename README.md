OSP7 Installer
---------------

Simple python wrapper around cobbler and ansible.


How to use it
==============

Clone this repo, `cd` into it.

```bash
ansible-playbook -i <inventory file for your environment> \
    installer/step1-provision-undercloud-server.yaml \
    installer/step2-install-osp10-undercloud.yaml \
    installer/step3-install-osp10-overcloud.yaml
```

Testbed Configuration
=====================

Physical Setup
--------------
### NICs
1. Controller NICs
    1. One nic for provisioning, external neutron network, and tenant networks

1. Compute NICs
    1. One nic for provisioning, and tenant networks

1. Undercloud Controller NICs
    1. undercloud_local_interface = <int, ie. enp9s0> -- this NIC is used for PXE'ing overcloud & provisioning access (tripleo-heat)
    1. undercloud_fake_gateway_interface: interface used for unrouted floating IP's (this will be the gateway if 'hack_in_undercloud_gateway_ip' == true) (native vlan must be set on port)

### Switch and UCSM Configs
1. Controller Nodes
  1. Native vlan configured to the provisioning VLAN
  1. trunk allowed vlan external neutron network and floating ip
  1. trunk allowed vlan for tenant vlan range
1. Compute Nodes
  1. Native vlan configured to the provisioning VLAN
  1. trunk allowed vlan for tenant vlan range

### Per-Testbed Settings (must set)

#### Create an ansible inventory file to describe the director node

```ini
[director]
<hostname or IP>
```

#### Populate information specific to that director's testbed

1. Alongside your inventory file create a directory `host_vars/`
1. In that directory create a new file named after your director node
1. Populate this file with your testbed specific information:

```yaml
---
cobbler_node_name:
cobbler_username:
cobbler_password:
cobbler_api_url:

dns_server_1:

undercloud_fake_gw_interface:
undercloud_fake_gw_cidr:

undercloud_local_ip_simple:
undercloud_local_ip_cidr:
undercloud_network_gateway:

overcloud_nodes:
  nodes:

overcloud_node_nic_mappings:

overcloud_control_scale:
overcloud_compute_scale:
overcloud_ceph_storage_scale:
overcloud_block_storage_scale:
overcloud_swift_storage_scale:

testbed_vlan:
storage_vlan:
storage_mgmt_vlan:
tenant_network_vlan:

overcloud_external_vlan:
overcloud_external_ip_cidr:
overcloud_external_ip_start:
overcloud_external_gateway:
overcloud_external_ip_end:
overcloud_director_ip:
overcloud_mask:

overcloud_floating_ip_cidr:
overcloud_floating_ip_start:
overcloud_floating_ip_end:
overcloud_floating_ip_network_gateway:

type_driver: vxlan,vlan,flat,gre
network_type: vlan
neutron_flat_networks: datacentre
neutron_external_bridge: br-ex

network_ucsm_ip:
network_ucsm_username:
network_ucsm_password:
network_ucsm_host_list:
network_ucsm_https_verify:

network_nexus_config:

network_nexus_managed_physical_network: datacentre
network_nexus_vlan_name_prefix: q-
network_nexus_svi_round_robin: false
network_nexus_provider_vlan_name_prefix: p-
network_nexus_persistent_switch_config: false
network_nexus_switch_heartbeat_time: 30
network_nexus_switch_replay_count: 10000
network_nexus_provider_vlan_auto_create: false
network_nexus_provider_vlan_auto_trunk: false
network_nexus_vxlan_global_config: false
network_nexus_host_key_checks: false
network_nexus_vlan_range: datacentre:<range>

vni_ranges: 0:0
mcast_ranges: 0.0.0.0:0.0.0.0

network_cntlr_mech_drivers:
  - openvswitch
  - cisco_ucsm
  - cisco_nexus

extra_neutron_config:
  ml2_cisco_ucsm/ucsm_https_verify:
    value: False
  ml2_cisco_ucsm/ucsm_virtio_eth_ports:
    value: ""
```

An example config can be found [here](installer/host_vars/bxb6-DIRECTOR)
