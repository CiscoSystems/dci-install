__author__ = 'brdemers'

# snippets used for ncclient, just to keep the ugly xml strings out of the way.

exec_conf_prefix = """
      <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
        <configure xmlns="http://www.cisco.com/nxos:1.0:vlan_mgr_cli">
          <__XML__MODE__exec_configure>
"""

exec_conf_postfix = """
          </__XML__MODE__exec_configure>
        </configure>
      </config>
"""

cmd_port_trunk = """
          <interface>
            <{type}>
              <interface>{port}</interface>
              <__XML__MODE_if-ethernet-switch>
                <description>
                  <value>{description}</value>
                </description>
                <switchport></switchport>
                <switchport>
                  <mode>
                    <trunk>
                    </trunk>
                  </mode>
                </switchport>
                <switchport>
                  <trunk>
                    <native>
                      <vlan>
                        <value>{native_vlan}</value>
                      </vlan>
                    </native>
                  </trunk>
                </switchport>
                <switchport>
                  <trunk>
                    <allowed>
                      <vlan>
                        <value>{testbed_vlan},{native_vlan},{storage_vlan},{storage_mgmt_vlan},{tenant_network_vlan}</value>
                      </vlan>
                    </allowed>
                  </trunk>
                </switchport>
              </__XML__MODE_if-ethernet-switch>
            </{type}>
          </interface>
"""

cmd_port_trunk_external = """
          <interface>
            <{type}>
              <interface>{port}</interface>
              <__XML__MODE_if-ethernet-switch>
                <description>
                  <value>{description}</value>
                </description>
                <switchport></switchport>
                <switchport>
                  <mode>
                    <trunk>
                    </trunk>
                  </mode>
                </switchport>
                <switchport>
                  <trunk>
                    <native>
                      <vlan>
                        <value>{native_vlan}</value>
                      </vlan>
                    </native>
                  </trunk>
                </switchport>
                <switchport>
                  <trunk>
                    <allowed>
                      <vlan>
                        <value>{native_vlan}</value>
                      </vlan>
                    </allowed>
                  </trunk>
                </switchport>
              </__XML__MODE_if-ethernet-switch>
            </{type}>
          </interface>
"""

cmd_vlan_create = """
            <vlan>
              <vlan-id-create-delete>
                <__XML__PARAM_value>{vlan_id}</__XML__PARAM_value>
                <__XML__MODE_vlan>
                  <name>
                    <vlan-name>{vlan_name}</vlan-name>
                  </name>
                </__XML__MODE_vlan>
              </vlan-id-create-delete>

              <vlan-id-create-delete>
                <__XML__PARAM_value>{vlan_id}</__XML__PARAM_value>
                <__XML__MODE_vlan>
                  <state>
                    <vstate>active</vstate>
                  </state>
                </__XML__MODE_vlan>
              </vlan-id-create-delete>

            </vlan>
"""
