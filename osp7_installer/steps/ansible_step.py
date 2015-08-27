__author__ = 'brdemers'

import step
import os
import ansible.runner
import ansible.inventory
import ansible.constants
from ansible.playbook import PlayBook
from ansible import callbacks
from ansible import utils
from ansible.utils import plugins

class AnsibleStep(step.Step):



    def execute(self, kargs):
        hosts = [kargs["director_node_ssh_ip"]]

        # ansible.constants.DEFAULT_HOST_LIST = hosts
        ansible.constants.HOST_KEY_CHECKING = False

        # load plugins, this will change in ansible 2
        module_dir = os.path.dirname(os.path.abspath(__file__))
        callback_dir = os.path.join(module_dir, '..', 'ansible_plugins')
        ansible.constants.DEFAULT_CALLBACK_PLUGIN_PATH = os.path.abspath(callback_dir)

        ansible_playbook = os.path.abspath(os.path.join(module_dir, '..', 'ansible', 'osp-director.yml'))

        plugins.callback_loader = plugins.PluginLoader(
            'CallbackModule',
            'ansible.callback_plugins',
            callback_dir,
            'callback_plugins'
        )

        inventory = ansible.inventory.Inventory(hosts)

        stats = callbacks.AggregateStats()
        # utils.VERBOSITY = 3
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)

        extra_vars = {}
        extra_vars.update(kargs)

        pb = ansible.playbook.PlayBook(
            playbook=ansible_playbook,
            # playbook="ansible/osp-director.yml",
            remote_user=kargs["director_node_ssh_username"],
            stats=stats,
            callbacks=playbook_cb,
            runner_callbacks=runner_cb,
            inventory=inventory,
            extra_vars= extra_vars
        )

        result = pb.run()
        print result
        print

        # plugins.callback_loader.
        for plugin in ansible.callbacks.callback_plugins:
            method = getattr(plugin, "playbook_on_stats", None)
            if method is not None:
                method(plugin)

        # check for failure
        for host, host_result in result.iteritems():
            if host_result['unreachable'] > 0 or host_result['failures']:
                raise Exception("Ansible step failure.")