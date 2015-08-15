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

Config example
===============

By default bootstrap.conf is loaded from the current working directory (override with `--config_file <config_file>` )

See bootstrap-example.conf (which is my actual config so do NOT use these IPs)

Other default config can be found in `osp7_installer/conf_common`

```
[DEFAULT]

director_node_hostname = direcotry-node.ctocllab.cisco.com
director_node_ssh_ip = 172.29.74.444

# requires ssh key on above node
director_node_ssh_username = root

[cobbler]
osp_directory_node = system-name-in-cobbler

[ansible]

# undercloud
undercloud_local_ip = 10.30.11.196/27
undercloud_local_interface = enp12s0
undercloud_masquerade_network = 10.30.11.192/27
undercloud_dhcp_start = 10.30.11.197
undercloud_dhcp_end = 10.30.11.216
undercloud_network_cidr = 10.30.11.192/27
undercloud_network_gateway = 10.30.11.193
undercloud_discovery_iprange = 10.30.11.217,10.30.11.222

# overcloud
overcloud_network_cidr = 192.168.0.0/16
overcloud_floating_ip_cidr = 10.30.1.48/28
overcloud_floating_ip_start = 10.30.1.52
overcloud_floating_ip_end = 10.30.1.62
overcloud_bm_network_gateway = 10.30.1.49

overcloud_nodes = {"nodes":[
                        {
                            "mac":[
                                "FF:FF:FF:FF:FF:FF"
                            ],
                            "cpu":"10",
                            "memory":"4096",
                            "disk":"60",
                            "arch":"x86_64",
                            "pm_type":"pxe_ipmitool",
                            "pm_user":"admin",
                            "pm_password":"passowrd",
                            "pm_addr":"172.29.74.111"
                       },
                       {
                           "mac":[
                                "FF:FF:FF:FF:FF:FF"
                            ],
                           "cpu":"10",
                           "memory":"4096",
                           "disk":"60",
                           "arch":"x86_64",
                           "pm_type":"pxe_ipmitool",
                           "pm_user":"admin",
                           "pm_password":"password",
                           "pm_addr":"172.29.74.222"
                       }
                  ]}

```

Currently this assumes RHEL, so it will try to register your server.
Add the following config properties to any config file, it is suggested you put them in `~/.osp7-installer/osp7.conf`

```
[ansible]
rhel_pool = <pool>
rhel_username = <username>
rhel_password = <password>
```



TODO
-----

Create example that stores config outside this repo, other then an example config, the default lap configs are still here.
Ideas:
  * move lab default configs to different project, and include that as a pip dependency,
  * move actual config to a different git repo, which basically just holds the config and a shell python project, to
include this project and the default lab config project.