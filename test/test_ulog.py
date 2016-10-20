#! /usr/bin/env python3
"""\
Tests for upathlib.
"""

import os
import unittest

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../device/flash/lib'))
import ulog


class TestHandler(object):
    def __init__(self):
        self.fmt = '{p} {x}{m}\n'
        self.messages = []

    def write_log(self, facility, priority, prefix, message):
        self.messages.append(self.fmt.format(p=ulog.prio_text[priority], x=prefix, m=message))


class Test_ulog(unittest.TestCase):

    def setUp(self):
        self._backup = ulog.handlers
        self.handler = TestHandler()
        ulog.handlers = [self.handler]

    def tearDown(self):
        ulog.handlers = self._backup

    def test_name(self):
        ulog.root.debug('debug 1')
        ulog.root.info('info 2')
        ulog.root.notice('notice 3')
        ulog.root.warn('warn 4')
        ulog.root.error('error 5')
        self.assertEqual(self.handler.messages, [
            'DEBUG debug 1\n',
            'INFO info 2\n',
            'NOTICE notice 3\n',
            'WARN warn 4\n',
            'ERROR error 5\n',
        ])


if __name__ == '__main__':
    unittest.main()
