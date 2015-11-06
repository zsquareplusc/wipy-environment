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
import glob
import io
import logging
import os
import sys


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
        """List files, meant for interactive use"""
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
        """Pipe (text) file contents to stdout, meant for interactive use"""
        try:
            self.log.debug('cat {}'.format(filename))
            self.ftp.retrlines("RETR " + filename, write_function)
        except ftplib.error_perm as e:
            self.log.error('invalid path: {} ({})'.format(filename, e))
        except ftplib.all_errors as e:
            self.log.error('FTP error: {}'.format(e))


WLANCONFIG_TEMPLATE = """\
ssid = '{ssid}'
password = '{password}'
"""

class WiPyActions(WiPyFTP):

    def install_lib(self):
        for filename in glob.glob('device/flash/lib/*.py'):
            with open(filename, 'rb') as src:
                self.put('/flash/lib/{}'.format(os.path.basename(filename)), src)

    def install_top(self):
        for filename in glob.glob('device/flash/*.py'):
            with open(filename, 'rb') as src:
                self.put('/flash/{}'.format(os.path.basename(filename)), src)

    def config_wlan(self):
        ssid = input('Enter SSID: ')
        password = input('Enter passphrase: ')
        self.put('/flash/wlanconfig.py',
                 io.BytesIO(WLANCONFIG_TEMPLATE.format(ssid=ssid, password=password).encode('utf-8')))

def main():
    import argparse

    parser = argparse.ArgumentParser(description='WiPy copy tool')

    parser.add_argument('action', help='Action to execute, try "help"')
    parser.add_argument('path', nargs='?', help='target used for some actions')
    parser.add_argument('-v', '--verbose', action='store_true', help='show more diagnostic messages')

    args = parser.parse_args()
    #~ print(args)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    with WiPyActions() as wipy:
        if args.action == 'ls':
            wipy.ls(args.path)
        elif args.action == 'sync-lib':
            wipy.install_lib()
        elif args.action == 'sync-top':
            wipy.install_top()
        elif args.action == 'initialize':
            wipy.install_top()
            wipy.install_lib()
            if input('Connect to an access point? [Y/n]: ').upper() in ('', 'Y'):
                wipy.config_wlan()

        elif args.action == 'config-wlan':
            print('Configure the WiPy to connect to an access point')
            wipy.config_wlan()

        elif args.action == 'cat':
            wipy.cat(args.path, print)
        #~ elif args.action == 'put':
            #~ wipy.put(args.path, ...)
        # option to set ssid/pw in wificonfig.txt

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()

