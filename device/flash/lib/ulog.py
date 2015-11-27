#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
A small loggin module.
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

#  facility codes
LOG_KERN      = 0       #  kernel messages
LOG_USER      = 1       #  random user-level messages
LOG_MAIL      = 2       #  mail system
LOG_DAEMON    = 3       #  system daemons
LOG_AUTH      = 4       #  security/authorization messages
LOG_SYSLOG    = 5       #  messages generated internally by syslogd
LOG_LPR       = 6       #  line printer subsystem
LOG_NEWS      = 7       #  network news subsystem
LOG_UUCP      = 8       #  UUCP subsystem
LOG_CRON      = 9       #  clock daemon
LOG_AUTHPRIV  = 10      #  security/authorization messages (private)
LOG_FTP       = 11      #  FTP daemon
LOG_LOCAL0    = 16      #  reserved for local use
LOG_LOCAL1    = 17      #  reserved for local use
LOG_LOCAL2    = 18      #  reserved for local use
LOG_LOCAL3    = 19      #  reserved for local use
LOG_LOCAL4    = 20      #  reserved for local use
LOG_LOCAL5    = 21      #  reserved for local use
LOG_LOCAL6    = 22      #  reserved for local use
LOG_LOCAL7    = 23      #  reserved for local use


class DefaultHandler(object):
    def __init__(self):
        self.fmt = '<{p}> {message}\n'

    def write_log(self, facility, priority, message):
        sys.stdout.write(self.fmt.format(p=(facility << 3) | priority, message=message))


class RSyslogHandler(DefaultHandler):
    #~ """https://tools.ietf.org/html/rfc5424"""
    def __init__(self, address):
        super().__init__()
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def write_log(self, facility, priority, message):
        self.socket.sendto(self.fmt.format(p=(facility << 3) | priority, message=message).encode('utf-8'), self.address)


handler = DefaultHandler()

class Logger(object):
    def __init__(self, facility=LOG_USER):
        self.facility = facility

    def debug(self, message):
        handler.write_log(self.facility, LOG_DEBUG, message)

    def info(self, message):
        handler.write_log(self.facility, LOG_INFO, message)

    def warn(self, message):
        handler.write_log(self.facility, LOG_WARN, message)

    def error(self, message):
        handler.write_log(self.facility, LOG_ERROR, message)

