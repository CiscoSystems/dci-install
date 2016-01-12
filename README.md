OSP7 Installer
---------------

Simple python wrapper around cobbler and ansible.


How to use it
==============

Clone this repo, `cd` into it.

```bash
$ virtualenv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python setup.py develop
$ osp7_bootstrap
```

For help see: `osp7_bootstrap --help`

Testbed Configuration
=====================

Physical Setup
--------------
All node types (controller, compute, ceph) need same NIC ordering due to use of per-node interface templates

### NICs
1. Controller NICs
    1. internal API / tenant nic (east/west) = neutron_private_nic
    1. external mgmt nic = neutron_public_nic (uses native vlan)
         1. this NIC gets the IP for the access to the mgmt network for Nexus & UCSM devices (ie. for mech drivers to use for netconf)
    1. neutron tenants' external network nic (north/south) = controller_floating_nic (uses native vlan)
1. Compute NICs
    1. internal API / tenant nic = hypervisor_neutron_public_nic
1. Undercloud Controller NICs
    1. undercloud_local_interface = <int, ie. enp9s0> -- this NIC is used for PXE'ing overcloud & provisioning access (tripleo-heat)
    1. undercloud_fake_gateway_interface: interface used for unrouted floating IP's (this will be the gateway if 'hack_in_undercloud_gateway_ip' == true) (native vlan must be set on port)

### Switch and UCSM Configs
1. undercloud PXE & provisioning/internal API 
    1. native VLAN set to the VLAN to use for PXE for all the following switchports/UCSM port config (called “undercloud_vlan” in osp7_install.py  base.conf)
         1. switchport connected to undercloud_local_interface 
         1. switchports connected to all other nodes internal ports
              1. nic indicated by hypervisor_neutron_public_nic
         1. allowed VLANs that need to be pre-configured on all internal nic switchports/UCSM config (see osp7_install base.conf):
              1. testbed_vlan
              1. storage_vlan
              1. storage_mgmt_vlan
              1. tenant_network_vlan (not really used)
              1. overcloud_floating_vlan
              1. overcloud_external_vlan
              1. undercloud_vlan
    1. external mgmt net
         1. configure native VLAN on switchport/UCSM port config for:
              1. switch/UCSM ports connected to controller mgmt net nics 
                   1. neutron_public_nic
    1. controller neutron external net (floating net)
         1. (optional) configure native VLAN on switchport/UCSM port config for:
              1. switch/UCSM ports connected to controller neutron tenant external net nics
                   1. controller_floating_nic
              1. NOTE: without this option:
                   1. the following bootstrap.conf settings should be used:
                        1. network_nexus_provider_vlan_auto_create = true
                        1. network_nexus_provider_vlan_auto_trunk = true
                   1. neutron net-create for external network should use VLAN type and segmentation ID of external vlan
                        1. not currently done in osp7_install
    
### Per-Testbed Settings (must set)
1. director_node_*
1. switch_*
1. osp_director_node
1. All NIC settings
    1. neutron_public_nic
    1. controller_floating_nic
    1. hypervisor_neutron_public_nic
    1. undercloud_local_interface
    1. undercloud_fake_gateway_interface (if using hack_in_undercloud_gateway_ip [default] )
1. VLANs
    1. overcloud_external_vlan
        1. override all osp7_install.py  base.conf VLAN settings:
    1. undercloud_vlan, etc
         * can use base.conf settings if you are the only OSPd testbed on a specific FI & switch*** (GG26 & BXB currently fall into this case)
1. overcloud_floating_ip_*
1. overcloud_external_* (needs to be routable, in order to have access to your switch/FI)
1. overcloud_nodes
1. network_nexus_config
1. network_ucsm_*


### Common settings
1. undercloud_* 
1. overcloud_external_*  
       - likely need to fully redeploy direcfor this to be true


Config example
===============

By default bootstrap.conf is loaded from the current working directory (override with `--config_file <config_file>` )

See bootstrap-example.conf (which is an actual config so do NOT use these IPs)

## Default Config
default config can be found in `osp7_installer/conf_common/base.conf`

There's an effort to converge as much of the config variables to the base.conf as possible
in order to minimize the bootstrap.conf settings for the most common testbed environments.

## Lab Location Specific Config
SJC and BXB common config can be found in the corresponding files in `osp7_installer/conf_common/[bxb|sj].conf`

Contents most likely to be:

1. http/https/etc proxy settings
1. cobbler server conf
     1. used for PXE'ing the OSP director node (undercloud director)


## Testbed Specific config

### Node Info
Each overcloud node needs an entry in the `overcloud_nodes` dictionary.  This info ends up in overcloud.json & is
used by the ironic node discovery phase of setup.

**NOTE:** the `capabilities` attribute is used to associate the node with a flavor. 

<pre>
overcloud_nodes = {"nodes":[
                   {
                      "mac":[
                          "00:25:b5:00:00:01"
                      ],
                      "capabilities": "profile:compute,boot_option:local",
                      "cpu":"10",
                      "memory":"4096",
                      "disk":"60",
                      "arch":"x86_64",
                      "pm_type":"pxe_ipmitool",
                      "pm_user":"openstack",
                      "pm_password":"openstack",
                      "pm_addr":"10.86.7.198"
                  },
                  {
                      "mac":[
                          "84:b8:02:8b:87:fe"
                      ],
                      "capabilities": "profile:control,boot_option:local",
                      "cpu":"10",
                      "memory":"4096",
                      "disk":"60",
                      "arch":"x86_64",
                      "pm_type":"pxe_ipmitool",
                      "pm_user":"openstack",
                      "pm_password":"openstack",
                      "pm_addr":"10.86.7.196"
                  },
                  ]}
</pre>

**Overcloud Deploy scale**
These settings are used only during overcloud deploy.  NOTE: more nodes than this can be in the ironic discovery.

<pre>
# scale of nodes
overcloud_control_scale = 3
overcloud_compute_scale = 1
</pre>

### NIC identifier

<pre>
# nic for br-ext on controller (north-south)
controller_floating_nic = nic3
# controller nic for mech drivers' nexus & ucsm management
neutron_public_nic = nic2
# controller nic for tenant east-west traffic & provisioning NIC
neutron_private_nic = nic1
#compute nic for tenant traffic & provisioning NIC
hypervisor_neutron_public_nic = nic1
</pre>

### Director Node config

<pre>
director_node_hostname = merc-control-2.bxb.os
director_node_ssh_ip = 10.86.7.199
director_node_ssh_username = root

# enp9s0 -> tor-2 eth1/29  (used for PXE)
# enp1s0f1 -> tor-1 eth1/20  (used to access overcloud external net)
undercloud_local_interface = enp9s0
undercloud_fake_gateway_interface = enp1s0f1

undercloud_fake_gw_ip = 172.17.35.49
undercloud_fake_gw_ip_prefix = 24

osp_directory_node = bxb-mercury-control-2
</pre>

**undercloud fake gateway**
Prefix for interface and IP settings for undercloud access to overcloud public API & possibly 
neutron tenants' external network (floating IP).  The "fake gw" could be a misnomer here but it 
_could_ be used for neutron tenants' external gateway. 

### IP config for undercloud controller & overcloud internal API
The IP addresses in the *base.conf* should be usable if the PXE/provisioning and internal API networks are isolated
to testbed private VLANs.  

The `undercloud*` IP addresses will be setup in undercloud.conf which get applied during undercloud deploy.  These
addresses get used mostly for *br_ctlplane* and one for a undercloud gateway interface. 

### Overcloud Public API net (external)
For a specific testbed the external and floating IPs are needed to be setup.

`overcloud_external_vlan`.
For the L2 networking to be used for the overcloud public API, the `overcloud_external_vlan` is used when 
osp7_bootstrap is to perform switch config (can be skipped if you preconfigure switches).  
NOTE: *nic-configs/controller.yaml* doesn't include *ExternalNetworkVlanID* in any bridge members.

**Overcloud Public/External IPs**
The following are applied either to `neutron_public_nic` or `br-ext` for the overcloud public API.  If 
 `controller_separate_public_nic` is *True* then `overcloud_external*` IPs are assigned to `neutron_public_nic`.
  Otherwise, they are assigned to `br-ext`.
 
<pre>
overcloud_external_ip_cidr = 172.17.32.0/20
overcloud_external_ip_start = 172.17.35.20
overcloud_external_ip_end = 172.17.35.48
overcloud_external_gateway = 172.17.32.1
</pre>

### Overcloud Floating IP net (default IPs for neutron's external network)
The overcloud floating IP net settings are used when osp7_bootstrap creates the neutron external network & subnet.

<pre>
overcloud_floating_ip_cidr = 172.17.32.0/20
overcloud_floating_ip_start = 172.17.35.52
overcloud_floating_ip_end = 172.17.35.252
overcloud_floating_ip_network_gateway = 172.17.32.1
</pre>

### Neutron general config
**Tenant net & VLAN range**
```network_nexus_vlan_range = datacentre:2010:2100```

**Mechanism Drivers**
```neutron_mechanism_drivers = openvswitch,cisco_nexus,cisco_ucsm```

### Configuration of the Nexus Switch
 **Limitation:**  Currently, osp7_bootstrap only supports configuring a single nexus switch per testbed. 
 
 **How-to skip:**  In your testbed's bootstrap.conf, add the following at the end:
 
  <pre>
  [switch_config]
 
  skip = true
  </pre>

 **Switch Info**
 
 <pre>
 switch_ssh_ip_address = 172.1.0.1
 switch_ssh_port = 22
 switch_username = admin
 switch_password = blah
 </pre>

 `physical_ports`.
 Used to specify node and port mappings to native VLAN switch config.
 **TBD**  Does this auto-include doing the trunk settings for the storage vlans, testbed_vlan, etc?
 
 `physical_ports_external`.
 Used to specify node and port mappings to native VLAN switch config.
 **TBD**  Does this auto-include doing the trunk settings for any other vlans?

### Nexus ML2 config

<pre>
network_nexus_config = { "bxb-mercury-tor-2" : {
                             "ip_address": "%(switch_ssh_ip_address)s",
                             "username": "%(switch_username)s",
                             "password": "%(switch_password)s",
                             "nve_src_intf": 0,
                             "ssh_port": %(switch_ssh_port)s,
                             "physnet": "datacentre",
                             "servers": {
                                 "%(node_2_mac)s": { "ports": "%(node_2_port)s,port-channel:1" },
				                 "%(node_3_mac)s": { "ports": "%(node_3_port)s,port-channel:1" },
				                 "%(node_4_mac)s": { "ports": "%(node_4_port)s,port-channel:1" },
                                                 "%(compute_1_mac)s": {"ports": "%(ucsm_fi_port)s" },
                             }
                         },
                       }
                       
network_nexus_provider_vlan_auto_create = false
network_nexus_provider_vlan_auto_trunk = false
</pre>

### UCSM ML2 config

<pre>
network_ucsm_ip = 10.86.7.69
network_ucsm_username = admin
network_ucsm_password = ***REMOVED***
network_ucsm_host_list = 00:25:b5:00:00:01:test,84:b8:02:5C:09:32:"",84:b8:02:8b:87:fe:"",84:b8:02:8b:9b:f6:""
</pre>

Known Problems
==============
1. Undercloud deployment--dib-run-parts failure: 

<pre>
WARNING: map-services has been deprecated.  Please use the svc-map element.
Failed to issue method call: Access denied
INFO: 2015-12-03 13:30:31,512 -- ############### End stdout/stderr logging ###############
ERROR: 2015-12-03 13:30:31,513 --     Hook FAILED.
ERROR: 2015-12-03 13:30:31,513 -- Failed running command ['dib-run-parts', u'/tmp/tmpvQ4HhO/pre-install.d']
</pre>
     1. Resolve by:
          1. rebooting the undercloud controller node manually and then
          2. rerun osp7_bootstrap deploy with `-p cobbler.skip=true`

TODO
-----

Create example that stores config outside this repo, other then an example config, the default lap configs are still here.
Ideas:
  * move lab default configs to different project, and include that as a pip dependency,
  * move actual config to a different git repo, which basically just holds the config and a shell python project, to
include this project and the default lab config project.