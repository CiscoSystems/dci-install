__author__ = 'brdemers'


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
              </__XML__MODE_if-ethernet-switch>
            </{type}>
          </interface>
"""