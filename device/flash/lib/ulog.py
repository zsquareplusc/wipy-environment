#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
A small logging module.
"""
import sys
import socket

# priorities
LOG_EMERG     = 0       #  system is unusable
LOG_ALERT     = 1       #  action must be taken immediately
LOG_CRIT      = 2       #  critical conditions
LOG_ERR       = 3       #  error conditions
LOG_WARNING   = 4       #  warning conditions
LOG_NOTICE    = 5       #  normal but significant condition
LOG_INFO      = 6       #  informational
LOG_DEBUG     = 7       #  debug-level messages

# facility codes
LOG_KERN      = 0o000   #  kernel messages
LOG_USER      = 0o010   #  random user-level messages
LOG_MAIL      = 0o020   #  mail system
LOG_DAEMON    = 0o030   #  system daemons
LOG_AUTH      = 0o040   #  security/authorization messages
LOG_SYSLOG    = 0o050   #  messages generated internally by syslogd
LOG_LPR       = 0o060   #  line printer subsystem
LOG_NEWS      = 0o070   #  network news subsystem
LOG_UUCP      = 0o100   #  UUCP subsystem
LOG_CRON      = 0o110   #  clock daemon
LOG_AUTHPRIV  = 0o120   #  security/authorization messages (private)
LOG_FTP       = 0o130   #  FTP daemon

prio_text = ('EMERG', 'ALERT', 'CRIT', 'ERROR', 'WARN', 'NOTICE', 'INFO', 'DEBUG')


class DefaultHandler(object):
    def __init__(self):
        self.fmt = '{p} {x}{m}\n'

    def write_log(self, facility, priority, prefix, message):
        sys.stdout.write(self.fmt.format(p=prio_text[priority], x=prefix, m=message))


class RSyslogHandler(object):
    """https://tools.ietf.org/html/rfc5424"""
    def __init__(self, address):
        self.fmt = '<{p}> {x}{m}'
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def write_log(self, facility, priority, prefix, message):
        self.socket.sendto(self.fmt.format(p=facility | priority, x=prefix, m=message).encode('utf-8'), self.address)


handlers = [DefaultHandler()]


class Logger(object):
    def __init__(self, prefix='', facility=LOG_USER):
        self.prefix = prefix
        self.facility = facility

    def log(self, priority, message):
        for handler in handlers:
            handler.write_log(self.facility, priority, self.prefix, message)

    def debug(self, message):
        self.log(LOG_DEBUG, message)

    def info(self, message):
        self.log(LOG_INFO, message)

    def notice(self, message):
        self.log(LOG_NOTICE, message)

    def warn(self, message):
        self.log(LOG_WARNING, message)

    def error(self, message):
        self.log(LOG_ERR, message)


root = Logger()


def add_remote(host, port=514):
    """Add remote syslog destination"""
    handlers.append(RSyslogHandler((host, port)))
