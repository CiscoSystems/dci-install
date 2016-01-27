__author__ = 'brdemers'

import logging

import steps
from config import Config
from bootstrap_steps import bootstrap_steps

class OspBoostrapCobbler(object):

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("bootstrap")
    logger.setLevel(logging.INFO)

    #
    def get_all_subclasses(self, klass):
        """Returns list of all known subclasses of 'klass'.
        This should probably not be done this way in python.  In other languages, this could easily pulled from an IoC
          Container.  I'm not sure, what the best way to do this is.
        :param klass: Gets list of all subclasses
        :return: A list of all subclasses of 'klass'
        """
        all_subclasses = {}

        for subclass in klass.__subclasses__():
            all_subclasses[subclass.__name__] = subclass
            all_subclasses.update(self.get_all_subclasses(subclass))

        return all_subclasses

    def all_steps(self):
        """Returns list of all known Step classes"""

        return self.get_all_subclasses(steps.Step)

    def execute_step(self, step_name, klass, kargs):
        """Executes Step against a set of configuration

        :param step_name: Name of step to run
        :param klass: Class that defines the step
        :param kargs: args to use as step input
        """

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

    def bootstrap(self, config_file, osp_version, lab_location, properties, action="deploy"):
        """

        :param config_file: path to config file which contains host specific information.
        :param lab_location: short labname string ['sj', 'bxb'].
        :param properties: Dictionary used to override config from 'config_file'.
        :param action: Key name of which set of steps to run ['deploy', 'redeploy'] see 'bootstrap_steps.py'
        """

        config = Config(config_file, osp_version, lab_location, properties)

        steps = self.all_steps()

        for step in bootstrap_steps[action]:
            if isinstance(step, basestring):
                self.execute_step(step, steps[step], config.get(step))
            else:
                # assume dict
                class_name = step.iterkeys().next()
                name = step.itervalues().next() or class_name

                self.execute_step( name, steps[class_name], config.get(name))

def main():
    """CLI method, run bootstrap.py --help to view."""
    import argparse
    parser = argparse.ArgumentParser(description='Ansible based utility to Bootstrap OSP7.')
    parser.add_argument('--config_file',
                        help='Path of config file.',
                        default="bootstrap.conf")
    parser.add_argument('--lab_location',
                        help='Location of testbed. [sj, bxb]',
                        default='sj')
    parser.add_argument('--osp_version',
                        help='Version of OSP to install and configure [7, 8]',
                        default='7')
    parser.add_argument('-p', '--property', action='append', default=[])

    parser.add_argument('--action',
                        help='Action [deploy, redeploy, test, update_image]',
                        default='deploy')

    args = parser.parse_args()

    extra_properties = {}

    for value in args.property:
        n, v = value.split('=')
        extra_properties[n] = v

    OspBoostrapCobbler().bootstrap(args.config_file, args.osp_version, args.lab_location, extra_properties, args.action)

if __name__ == '__main__':
    main()

