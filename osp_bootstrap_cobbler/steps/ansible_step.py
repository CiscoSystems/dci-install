__author__ = 'brdemers'

import step
import os
import ansible.runner
import ansible.inventory
import ansible.constants
from ansible.playbook import PlayBook
from ansible import callbacks
from ansible import utils

class AnsibleStep(step.Step):



    def execute(self, kargs):
        hosts = [kargs["director_node_ssh_ip"]]

        # ansible.constants.DEFAULT_HOST_LIST = hosts
        ansible.constants.HOST_KEY_CHECKING = False

        # load plugins, this will change in ansible 2
        module_dir = os.path.dirname(os.path.abspath(__file__))
        callback_dir = os.path.join(module_dir, '..', 'ansible_callback_plugins')
        ansible.constants.DEFAULT_CALLBACK_PLUGIN_PATH = os.path.abspath(callback_dir)

        inventory = ansible.inventory.Inventory(hosts)

        stats = callbacks.AggregateStats()
        # utils.VERBOSITY = 3
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)

        extra_vars = {}
        extra_vars.update(kargs)

        pb = ansible.playbook.PlayBook(
            playbook="ansible/osp-director.yml",
            remote_user=kargs["director_node_ssh_username"],
            stats=stats,
            callbacks=playbook_cb,
            runner_callbacks=runner_cb,
            inventory=inventory,
            extra_vars= extra_vars
        )

        result = pb.run()
        print result
