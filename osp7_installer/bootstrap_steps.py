__author__ = 'brdemers'

#
#
bootstrap_steps = {

    "deploy": [
        # { "ExampleStep": 'example' },
        # { "AnsibleStep": 'rhel_unregister' },
        { "SwitchConfigStep": 'switch_config' },
        {"CobblerOSInstallStep": "cobbler"},
        {"AnsibleStep": "ansible"},
    ],
    "redeploy": [
        { "SwitchConfigStep": "switch_config" },
        { "AnsibleStep": "redeploy" },
    ],
    "test": [
        { "AnsibleStep": "test_cloud" },
    ],
    "noop": [
        { "ExampleStep": 'example' },
    ]
}
"""Mapping of 'actions' to steps, This allows for mixing python and ansible runs together sequentially.
It is possible that all these steps could be converted to ansible tasks/playbooks given time and understanding, but it
is also easy to just include a few lines of python to accomplish what you need.

NOTE: writing things in python instead of Ansible directly should NOT be abused, the intent was to use python for
preconfig steps (switch config, re-installation via cobbler, etc)

The format is: { "action": [{"StepClass1": "config_section_name"}]}
"""