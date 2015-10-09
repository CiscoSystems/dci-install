__author__ = 'brdemers'

import step

class ExampleStep(step.Step):
    """
    Simple example step just to show the plumbing of a step to executing random code.
    """

    def execute(self, kargs):
        """Prints all arguments passed to step."""
        print "all variables: {}".format(kargs)
        