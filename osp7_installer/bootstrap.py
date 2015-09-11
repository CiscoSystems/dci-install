__author__ = 'brdemers'

import logging

import steps
from config import Config
from bootstrap_steps import bootstrap_steps

class OspBoostrapCobbler(object):

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("bootstrap")
    logger.setLevel(logging.INFO)

    def get_all_subclasses(self, klass):
        all_subclasses = {}

        for subclass in klass.__subclasses__():
            all_subclasses[subclass.__name__] = subclass
            all_subclasses.update(self.get_all_subclasses(subclass))

        return all_subclasses

    def all_steps(self):
        return self.get_all_subclasses(steps.Step)

    def execute_step(self, step_name, klass, kargs):

        self.logger.debug("Executing Step %(step_name)s, with class: %(klass)s, and args: %(kargs)s", {'step_name': step_name, 'klass': klass, 'kargs': kargs})

        if not kargs['skip']:
            self.logger.info("Executing step " + step_name)

            if kargs['ignore_errors']:
                try:
                    klass().execute(kargs)
                except Exception as e:
                    print "Ignoring step failure: ", e
            else:
                klass().execute(kargs)

        else:
            self.logger.info("Skipping step " + step_name)

    def bootstrap(self, config_file, lab_location, properties):

        config = Config(config_file, lab_location, properties)

        steps = self.all_steps()

        for step in bootstrap_steps:
            if isinstance(step, basestring):
                self.execute_step(step, steps[step], config.get(step))
            else:
                # assume dict
                class_name = step.iterkeys().next()
                name = step.itervalues().next() or class_name

                self.execute_step( name, steps[class_name], config.get(name))

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Ansible based utility to Bootstrap OSP7.')
    parser.add_argument('--config_file',
                        help='Path of config file.',
                        default="bootstrap.conf")
    parser.add_argument('--lab_location',
                        help='Location of testbed. [sj, bxb]',
                        default='sj')
    parser.add_argument('-p', '--property', action='append', default=[])

    args = parser.parse_args()

    extra_properties = {}
    for value in args.property:
        n, v = value.split('=')
        extra_properties[n] = v

    OspBoostrapCobbler().bootstrap(args.config_file, args.lab_location, extra_properties)

if __name__ == '__main__':
    main()

