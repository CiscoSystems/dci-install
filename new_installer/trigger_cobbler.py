import argparse
import logging
import uuid
import xmlrpclib


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def reboot(ci_key, args):
    """Updates netboot key and reboots Server via cobbler.

    :param ci_key: unique key used to identify the kickstart was successful.
    :param args: Args for cobbler connection info
    """

    director_node = args.cobbler_node_name
    server = xmlrpclib.Server(args.cobbler_api_url)
    token = server.login(args.cobbler_username, args.cobbler_password)

    LOG.info("Reboot/install: {}".format(director_node))

    # enable PXE Boot
    system_handle = server.get_system_handle(director_node, token)
    server.modify_system(system_handle, "netboot_enabled", True, token)
    server.modify_system(system_handle, "ks_meta", "ci_key={}".format(ci_key), token)
    server.sync(token)

    # reboot
    system_handle = server.get_system_handle(director_node, token)
    server.power_system(system_handle, "reboot", token)
    server.sync(token)


parser = argparse.ArgumentParser(description='Reboot a cobbler node to deploy it')
parser.add_argument('cobbler_api_url', type=str)
parser.add_argument('cobbler_username', type=str)
parser.add_argument('cobbler_password', type=str)
parser.add_argument('cobbler_node_name', type=str)


if __name__ == "__main__":
    args = parser.parse_args()
    ci_key = str(uuid.uuid4())
    reboot(ci_key, args)
    print(ci_key)
