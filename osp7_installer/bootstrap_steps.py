__author__ = 'brdemers'


bootstrap_steps = {

    "default": [
        # { "ExampleStep": 'example' },
        { "AnsibleStep": 'rhel_unregister' },
        { "SwitchConfigStep": 'switch_config' },
        {"CobblerOSInstallStep": "cobbler"},
        {"AnsibleStep": "ansible"},
    ],
    "redeploy": [
        # TODO: create overcloud delete step
        { "SwitchConfigStep": 'switch_config' },
        {"AnsibleStep": "ansible"},
    ]
}