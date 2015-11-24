__author__ = 'brdemers'

import step
import logging
import ncclient.manager as manager
import ncclient_snippets as snip

class SwitchConfigStep(step.Step):
    """Configures switch ports with some basic defaults, used by the under and overclouds."""

    logger = logging.getLogger("switch_config_step")
    logger.setLevel(logging.DEBUG)

    def _edit_config(self, mgr_conn, command_snippet):
        confstr = snip.exec_conf_prefix + command_snippet + snip.exec_conf_postfix
        mgr_conn.edit_config(target='running', config=confstr)

    def execute(self, kargs):
        """Configures switch ports with some basic defaults, used by the under and overclouds."""

        connection = manager.connect(host=kargs["switch_ssh_ip_address"],
                                     port=kargs["switch_ssh_port"],
                                     username=kargs["switch_username"],
                                     password=kargs["switch_password"],
                                     hostkey_verify=False,
                                     device_params={"name": "nexus"})
        try:
            vlans = {
                'OSP-Testbed': kargs['testbed_vlan'],
                'OSP-Storage': kargs['storage_vlan'],
                'OSP-Storage-Mgmt': kargs['storage_mgmt_vlan'],
                'OSP-Tenant-Network': kargs['tenant_network_vlan'],
                'OSP-Undercloud': kargs['undercloud_vlan'],
                'OSP-Overcloud-Ext': kargs['overcloud_external_vlan'],

            }
            for vlan_name, vlan_id in vlans.iteritems():
                self.logger.debug("Creating vlan %s: %s", vlan_name, vlan_id )
                self._edit_config(connection, snip.cmd_vlan_create.format(vlan_id=vlan_id, vlan_name=vlan_name))


            for switchport in kargs["physical_ports"]:
                self.logger.debug("Configuring nic %s, for native vlan: %s, and vlans: %s", switchport['port'], switchport['native_vlan'],[ kargs['testbed_vlan'],kargs['storage_vlan'],kargs['storage_mgmt_vlan'],kargs['tenant_network_vlan']] )
                self._edit_config(connection, snip.cmd_port_trunk.format(type="ethernet",
                                                                         port=switchport['port'],
                                                                         native_vlan=switchport['native_vlan'],
                                                                         testbed_vlan=kargs['testbed_vlan'],
                                                                         overcloud_vlan=kargs['overcloud_vlan'],
                                                                         overcloud_external_vlan=kargs['overcloud_external_vlan'],
                                                                         storage_vlan=kargs['storage_vlan'],
                                                                         storage_mgmt_vlan=kargs['storage_mgmt_vlan'],
                                                                         tenant_network_vlan=kargs['tenant_network_vlan'],
                                                                         description=switchport['description'] ))
            for switchport in kargs["physical_ports_external"]:
                self.logger.debug("Configuring external nic %s, for vlan: %s", switchport['port'], switchport['native_vlan'])
                self._edit_config(connection, snip.cmd_port_trunk_external.format(type="ethernet",
                                                                                  port=switchport['port'],
                                                                                  native_vlan=switchport['native_vlan'],
                                                                                  description=switchport['description'] ))

        finally:
            connection.close_session()


