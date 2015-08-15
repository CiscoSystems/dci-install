__author__ = 'brdemers'

import step
import xmlrpclib
import uuid
import time
import paramiko
import logging
import socket

class CobblerOSInstallStep(step.Step):

    logger = logging.getLogger("cobbler_os_install")
    logger.setLevel(logging.DEBUG)

    def reboot(self, ci_key, kargs):

        director_node = kargs["osp_directory_node"]
        server = xmlrpclib.Server(kargs["cobbler_api_url"])
        token = server.login(kargs["cobbler_username"],kargs["cobbler_password"])

        # enable PXE Boot
        system_handle = server.get_system_handle(director_node, token)
        server.modify_system(system_handle, "netboot_enabled", True, token)
        server.modify_system(system_handle,"ks_meta", "ci_key={}".format(ci_key), token)
        server.sync(token)

        # reboot
        system_handle = server.get_system_handle(director_node, token)
        server.power_system(system_handle, "reboot", token)
        server.sync(token)

    def poll_for_server(self, ssh_ip, ssh_user, ci_key):
        poll_interval = 30
        poll_times = 60 # 30 min max


        self.logger.info("Testing connection to: "+ ssh_ip)

        for attempt in range(poll_times):

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                ssh.connect(ssh_ip, username=ssh_user, timeout=5)
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("cat /etc/ci-key")

                # read the output
                output = ssh_stdout.read().strip()
                err_output = ssh_stderr.read()

                # close the connection
                ssh.close()

                # if we have the ci_key we are looking for just return
                self.logger.debug("expected ci-key: '{}'".format(ci_key))
                self.logger.debug("actual ci-key:   '{}'".format(output))
                if output == ci_key:
                    return True

                # otherwise, wait and try again
                if err_output:
                    self.logger.debug("ssh command returned error: "+ err_output)

            except paramiko.SSHException:
                self.logger.debug("Failed to connect on attempt {} of {}".format(attempt, poll_times))
            except socket.timeout:
                self.logger.debug("Failed to connect on attempt {} of {}".format(attempt, poll_times))
            except socket.error:
                self.logger.debug("Failed to connect on attempt {} of {}".format(attempt, poll_times))

            # try again after waiting
            time.sleep(poll_interval)

        # server never responded
        return False


    def execute(self, kargs):

        ci_key = str(uuid.uuid4())

        self.reboot(ci_key, kargs)
        # wait after issuing reboot before starting to poll
        time.sleep(60)

        print self.poll_for_server(kargs["director_node_ssh_ip"], kargs["director_node_ssh_username"], ci_key)


