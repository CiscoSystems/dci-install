__author__ = 'brdemers'


bootstrap_steps = {

    "deploy": [
        # { "ExampleStep": 'example' },
        { "AnsibleStep": 'rhel_unregister' },
        { "SwitchConfigStep": 'switch_config' },
        {"CobblerOSInstallStep": "cobbler"},
        {"AnsibleStep": "ansible"},
    ],
    "redeploy": [
        { "AnsibleStep": "redeploy" },
        { "SwitchConfigStep": "switch_config" },
        { "AnsibleStep": "ansible" },
    ]
}