#! /usr/bin/env python

from ironicclient import client
import os
import sys

search_addr = sys.argv[1]

kwargs = {'os_username': os.environ['OS_USERNAME'],
          'os_password': os.environ['OS_PASSWORD'],
          'os_auth_url': os.environ['OS_AUTH_URL'],
          'os_tenant_name': os.environ['OS_TENANT_NAME']}

ironic = client.get_client(1, **kwargs)

for node in ironic.node.list():
    node = ironic.node.get(node.uuid)
    if search_addr == node.driver_info['ipmi_address']:
        print node.uuid
        exit
exit(1)