#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Simple rsyslog (subset thereof) viewer.
"""
import datetime
import logging
import re
import socket
import sys

prio_text = ('EMERG', 'ALERT', 'CRIT', 'ERR', 'WARN', 'NOTICE', 'INFO', 'DEBUG')

re_syslog = re.compile(r'<(?P<pri>\d+)> (?P<msg>.*)')  # XXX simplified subset


def log_receiver(output, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    logging.info("Press CTRL+C to exit")
    while True:
        data, address = sock.recvfrom(65507)
        if data:
            m = re_syslog.match(data.decode('utf-8'))
            if m is not None:
                pri = int(m.group('pri'))
                priority = pri & 7
                facility = pri >> 3
                output.write('{d:%Y-%m-%d %H:%M} {a[0]}:{a[1]} : {p} {m!r}\n'.format(
                        d=datetime.datetime.now(),
                        a=address,
                        p=prio_text[priority],
                        m=m.group('msg')))
            else:
                output.write('{d:%Y-%m-%d %H:%M} {a[0]}:{a[1]} failed to decode : {m!r}\n'.format(
                        d=datetime.datetime.now(),
                        a=address,
                        m=data))
            output.flush()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def main():
    import argparse

    parser = argparse.ArgumentParser(
            description='logviewer too for WiPy ulog module (rsyslog compatible)')

    parser.add_argument('-v', '--verbose', action='store_true', help='show more diagnostic messages')
    parser.add_argument('-p', '--port', default=5140, type=int, help='specify UDP port to listen to (default: %(default)s)')

    args = parser.parse_args()
    #~ print(args)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    try:
        log_receiver(sys.stdout, args.port)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        logging.info("Exit")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__":
    main()
