###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

import sys, os, shutil
from datetime import datetime
#from mapping import TARTAROS_LOGGING_PATH

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

LEVELS = {
    'info':     0,
    'debug':    1,
    'trace':    2,
    'warn':     1,
    'error':    0,
}
TEST_STATUSES = {
    'passed':           'passed',
    'failed':           'failed',
    'blocked':          'blocked',
    're-test':          're-test',
    'not tested':       'not tested',
    'passed with issues':'passed with issues',
    'invalid due to version':'invalid due to version',
}

####################################################################################################
# Logger ###########################################################################################
####################################################################################################
####################################################################################################


class Logger():
    """ Library for logging messages. """

    def __init__(
            self, logging_level='trace', output_path=os.getcwdu() + "\\logs",
            output_filename="Tartaros.log"):

        self.logging_level = LEVELS[logging_level.lower()]

        # validate output path
        self.output_path = output_path
        self.output_filename = output_filename
        try:
            if not os.path.exists(self.output_path):
                self.output_path = None
                sys.stderr.write("Failed to validate output path: '%s'." % self.output_path)
            if os.path.exists(self.output_path + "\\" + self.output_filename):
                self.archive_active_logging_file()

        except BaseException, e:
            sys.stderr.write("Failed to handle output path.")
            sys.stderr.write(str(e))
            self.output_path = None
            self.output = None

        # logger tracking
        self.active_output_start = datetime.now().day

    def log_message(self, message, level, new_line=True):
        """ Log message according to level. """

        # define message to log
        message_to_log = str(message)

        # modify message depending on level
        if not new_line:
            sys.stdout.write(message_to_log)
        elif level == 'info' and self.logging_level >= LEVELS['info']:
            message_to_log = '\033[95m*INFO*\t' + message_to_log
        elif level == 'debug' and self.logging_level >= LEVELS['debug']:
            message_to_log = '\033[94m*DEBUG*\t\t' + message_to_log
        elif level == 'trace' and self.logging_level >= LEVELS['trace']:
            message_to_log = '\033[92m*TRACE*\t\t\t' + message_to_log
        elif level == 'warn' and self.logging_level >= LEVELS['warn']:
            message_to_log = '\033[93m*WARN*\t\t' + message_to_log
        elif level == 'error' and self.logging_level >= LEVELS['error']:
            message_to_log = '\033[91m*ERROR*\t' + message_to_log
        else:
            message_to_log = None

        if message_to_log is not None and new_line:
            # append datetime
            message_to_log = str(datetime.now()) + ' ' + message_to_log

            # add \n
            message_to_log = '\n' + message_to_log

            # write message to log
            sys.stdout.write(message_to_log)
            #if level == 'warn' or level == 'error':
            #    sys.stderr.write(message_to_log)

            try:
                if self.output_path is not None:
                    # check for roll-over at end of day
                    if datetime.now().day > self.active_output_start:
                        self.archive_active_logging_file()

                    # append output
                    self.output = open(self.output_path + "\\" + self.output_filename, 'a')
                    self.output.write(message_to_log)
                    self.output.close()

            except BaseException, e:
                sys.stderr.write("Failed to write to output file.")
                sys.stderr.write(str(e))
    def archive_active_logging_file(self):
        try:
            filepath = self.output_path + "\\" + self.output_filename
            filepath_list = filepath.split('.')
            filepath_list[0] += str(datetime.now()).replace(' ', '_').replace(':', '_').replace('.', '_')
            new_filepath = '.'.join(filepath_list)
            shutil.move(filepath, new_filepath)
        except BaseException, e:
            sys.stderr.write(str(e))

    def info(self, message):
        self.log_message(message, 'info')

    def debug(self, message):
        self.log_message(message, 'debug')

    def trace(self, message):
        self.log_message(message, 'trace')

    def warn(self, message):
        self.log_message(message, 'warn')
        self.build_error(message)

    def error(self, message):
        self.log_message(message, 'error')
        self.build_error(message)

    def trace_in_line(self, message):
        self.log_message(message, 'trace', new_line=False)

    def build_error(self, message):
        """ Send an error message to TeamCity.
        The error message will be included in the parent test case stacktrace if it fails.
        """

        message = "\n##teamcity[message text='%s' errorDetails='' status='ERROR']" % message
        print message

    def build_test_start(self, test_name):
        """ Send service message to TeamCity that test with specified name is beginning.
        This tells TeamCity that all subsequent test cases are included within the specified
        test until a test ending message is received.
        """

        message = "\n##teamcity[testSuiteStarted name='%s']" % test_name
        print message

    def build_test_end(self, test_name):
        """ Send service message to TeamCity that test case with specified name is ending.
        This tells TeamCity to stop associating test cases with the specified test.
        """

        message = "\n##teamcity[testSuiteFinished name='%s']" % test_name
        print message

    def build_testcase_start(self, name):
        """ Send service message to TeamCity that test case with specified name is beginning.
        This tells TeamCity that all subsequent messages should be associated with the
        specified test case until a test case ending message is received. """

        message = "\n##teamcity[testStarted name='%s']"%name
        print message

    def build_testcase_end(self, test_name, status, duration, stacktrace=None):
        """ Send service message to TeamCity that test case with specified name is ending.
        This tells TeamCity to stop associating messages with the specified test case.
        INPUT
            status: should be PASS or FAIL.
            duration: should be an integer.
            stacktrace: should be a string containing any relevant logging for errors.
        """

        # if test case failed, send test failure service message to TeamCity
        if status.lower() != TEST_STATUSES['passed']:
            # include stacktrace if available
            if stacktrace is not None:
                failureMessage = "\n##teamcity[testFailed name='%s' details='%s']"\
                                 % (test_name, stacktrace)
            else: failureMessage = "\n##teamcity[testFailed name='%s']" % test_name
            print failureMessage

        # convert seconds (recorded duration) to milliseconds (TeamCity)
        duration *= 1000
        message = "\n##teamcity[testFinished name='%s' duration='%d']" % (test_name, duration)
        print message

    def build_set_label(self, label, version):
        """ Send service message to TeamCity that the build should have the given label.
        INPUT
            label: the string to identify the build object (usually name, e.g., test name).
            version: the version of the product under test.
        """

        message = "##teamcity[buildNumber '%s-%s']" % (str(version), label)
        print message