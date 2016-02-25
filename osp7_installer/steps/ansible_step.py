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
    """Executes an Ansible playbook."""

    def execute(self, kargs):
        """
        Runs an Ansible playbook.
        :param kargs: arguments used in this step, all args are passed directly to Ansible
        """
        hosts = [kargs["director_node_ssh_ip"]]

        ssh_conf_file = "{base_dir}/ssh.config.ansible".format(base_dir=os.getcwd())

        # create the file if it does not exist (should do this in ansible with a local action)
        if not os.path.isfile(ssh_conf_file):
            with open(ssh_conf_file, 'a'):
                os.utime(ssh_conf_file, None)

        # Dynamic hosts change keys, so ignore that.
        ansible.constants.HOST_KEY_CHECKING = False
        ansible.constants.ANSIBLE_SSH_ARGS = "-F {ssh_conf_file}".format(ssh_conf_file=ssh_conf_file)

        # load plugins, this will change in ansible 2
        module_dir = os.path.dirname(os.path.abspath(__file__))
        callback_dir = os.path.join(module_dir, '..', 'ansible_plugins')
        ansible.constants.DEFAULT_CALLBACK_PLUGIN_PATH = os.path.abspath(callback_dir)

        # Only use playbooks in a known location"
        ansible_playbook = os.path.abspath(os.path.join(module_dir, '..', 'ansible', kargs["playbook"]))

        # Configure the plugin loader, along with a custom 'profile_tasks' plugin (for timing info)
        plugins.callback_loader = plugins.PluginLoader(
            'CallbackModule',
            'ansible.callback_plugins',
            callback_dir,
            'callback_plugins'
        )

        # an inventory is required, for now this will always be a single node.
        inventory = ansible.inventory.Inventory(hosts)
        stats = callbacks.AggregateStats()

        # enable debug if 'debug' is set (from CLI this would be '-p ansible.debug=true')
        if "debug" in kargs and kargs["debug"] is True:
            utils.VERBOSITY = 3

        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)

        # add all the properties passed into the step
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

        # Run it!
        result = pb.run()
        # Print the results, just to be verbose
        print result
        print


        # Our custom stats plug will print stats to the console, other stats plugins would also be collected here.
        for plugin in ansible.callbacks.callback_plugins:
            method = getattr(plugin, "playbook_on_stats", None)
            if method is not None:
                method(plugin)

        # check for failure, if so, fail the step
        for host, host_result in result.iteritems():
            if host_result['unreachable'] > 0 or host_result['failures']:
                raise Exception("Ansible step failure.")