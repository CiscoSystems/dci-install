__author__ = 'brdemers'

import step

class ExampleStep(step.Step):

    def execute(self, kargs):
        print "all variables: {}".format(kargs)
        