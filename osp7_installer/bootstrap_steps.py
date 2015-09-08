__author__ = 'brdemers'


bootstrap_steps = [

    # { "ExampleStep": 'example' },
    { "AnsibleStep": 'rhel_unregister' },
    { "SwitchConfigStep": 'switch_config' },
    {"CobblerOSInstallStep": "cobbler"},
    {"AnsibleStep": "ansible"},

]