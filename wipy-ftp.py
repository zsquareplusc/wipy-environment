#! /usr/bin/env python3
# encoding: utf-8
"""\
WiPy helper tool to access file via FTP.

For configuration, a file called ``wipy-ftp.ini`` must be present with the following contents:

    [FTP]
    server = 192.168.1.1
    user = micro
    pass = python

Adapt as needed when connected via router.
"""
import configparser  # https://docs.python.org/3/library/configparser.html
import ftplib        # https://docs.python.org/3/library/ftplib.html
import sys
import logging


class WiPyFTP(object):
    def __init__(self):
        self.ftp = None
        self.log = logging.getLogger('FTP')
        self.config = configparser.RawConfigParser()
        self.config.read('wipy-ftp.ini')

    def __enter__(self):
        self.log.debug('Connecting...')
        self.ftp = ftplib.FTP(self.config['FTP']['server'])
        self.ftp.login(self.config['FTP']['user'], self.config['FTP']['pass'])
        self.log.debug('Connection OK')
        return self

    def __exit__(self, *args, **kwargs):
        self.log.debug('Disconnecting...')
        self.ftp.quit()

    def ls(self, path=None):
        if path is None:
            path = '/'
        try:
            self.ftp.cwd(path)
            self.log.debug('ls {}'.format(self.ftp.pwd()))
            print(self.ftp.retrlines('LIST'))
        except ftplib.error_perm as e:
            self.log.error('invalid path: {} ({})'.format(path, e))
        except ftplib.all_errors as e:
            self.log.error('FTP error: {}'.format(e))

    def put(self, filename, fileobj):
        try:
            self.log.info('put {}'.format(filename))
            self.ftp.storbinary("STOR " + filename, fileobj, 1024)
        except ftplib.error_perm as e:
            self.log.error('invalid path: {} ({})'.format(filename, e))
        except ftplib.all_errors as e:
            self.log.error('FTP error: {}'.format(e))

    def get(self, filename, fileobj):
        try:
            self.log.info('get {}'.format(filename))
            self.ftp.retrbinary("RETR " + filename, fileobj.write, 1024)
        except ftplib.error_perm as e:
            self.log.error('invalid path: {} ({})'.format(filename, e))
        except ftplib.all_errors as e:
            self.log.error('FTP error: {}'.format(e))

    def cat(self, filename, write_function):
        try:
            self.log.debug('cat {}'.format(filename))
            self.ftp.retrlines("RETR " + filename, write_function)
        except ftplib.error_perm as e:
            self.log.error('invalid path: {} ({})'.format(filename, e))
        except ftplib.all_errors as e:
            self.log.error('FTP error: {}'.format(e))


def main():
    import argparse
    import glob
    import os


    parser = argparse.ArgumentParser(description='WiPy copy tool')

    parser.add_argument('action', help='Action to execute, try "help"')
    parser.add_argument('path', nargs='?', help='target used for some actions')
    parser.add_argument('-v', '--verbose', action='store_true', help='show more diagnostic messages')

    args = parser.parse_args()
    #~ print(args)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    with WiPyFTP() as wipy:
        if args.action == 'ls':
            wipy.ls(args.path)
        elif args.action == 'sync-lib':
            for filename in glob.glob('device/flash/lib/*.py'):
                with open(filename, 'rb') as src:
                    wipy.put('/flash/lib/{}'.format(os.path.basename(filename)), src)
        elif args.action == 'sync-top':
            for filename in glob.glob('device/flash/*.py'):
                with open(filename, 'rb') as src:
                    wipy.put('/flash/{}'.format(os.path.basename(filename)), src)

        elif args.action == 'cat':
            wipy.cat(args.path, print)
        #~ elif args.action == 'put':
            #~ wipy.put(args.path, ...)
        # option to set ssid/pw in wificonfig.txt

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()

