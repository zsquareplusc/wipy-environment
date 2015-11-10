#! /usr/bin/env python3
# encoding: utf-8
"""\
WiPy helper tool to access file via FTP.

Usage: wipy-ftp.py [-v --defaults] ACTION [ARGS]

  -v, --verbose     print more diagnostic messages
  --defaults        ignore .ini file and use defaults

ACTIONS are:
- "write-ini" create ``wipy-ftp.ini`` with default settings
- "install"  copy boot.py, main.py and /lib from the PC to the WiPy
- "sync-lib" copies only /lib
- "sync-top" copies only boot.py, main.py
- "config-wlan" ask for SSID/Password and write wlanconfig.py on WiPy
- "ls" with optional path argument: list files
- "cat" with filename: show text file contents
- "upgrade"  write mcuimg.bin file to WiPy for firmware upgrade
- "help"  this text

For configuration, a file called ``wipy-ftp.ini`` must be present with the
following contents, run "wipy-ftp.py write-ini" to create one.
Adapt as needed when connected via router.
"""
import configparser  # https://docs.python.org/3/library/configparser.html
import ftplib        # https://docs.python.org/3/library/ftplib.html
import glob
import io
import logging
import os
import sys

INI_TEMPLATE = """\
[FTP]
server = 192.168.1.1
user = micro
pass = python
"""


class WiPyFTP(object):
    def __init__(self, read_ini=True):
        self.ftp = None
        self.log = logging.getLogger('FTP')
        self.config = configparser.RawConfigParser()
        self.config.read_string(INI_TEMPLATE)
        if read_ini:
            self.config.read('wipy-ftp.ini')
        self.log.debug('WiPy IP: {}'.format(self.config['FTP']['server']))
        self.log.debug('FTP user: {}'.format(self.config['FTP']['user']))
        self.log.debug('FTP pass: {}'.format(self.config['FTP']['pass']))

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

    def mkdir(self, dirname):
        try:
            self.log.info('mkdir {}'.format(dirname))
        except ftplib.error_perm as e:
            self.log.error('invalid path: {} ({})'.format(dirname, e))
        except ftplib.all_errors as e:
            self.log.error('FTP error: {}'.format(e))

    def chdir(self, dirname):
        try:
            self.log.info('chdir {}'.format(dirname))
        except ftplib.error_perm as e:
            self.log.error('invalid path: {} ({})'.format(dirname, e))
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
        base_path = 'device/flash/lib'
        for root, dirs, files in os.walk(base_path):
            path = os.path.relpath(root, base_path).split(os.sep)
            for dir_name in path[0:-1]:
                print('chdir', dir_name)
                self.chdir(dir_name)
            if path != ['.'] and path[-1]:
                print('mkdir', path[-1])
                self.mkdir(path[-1])
                print('chdir', path[-1])
                self.chdir(path[-1])
            for filename in files:
                with open(os.path.join(root, filename), 'rb') as src:
                    print('put', filename)
                    self.put('/flash/{}'.format(filename), src)
            if path != ['.'] and path[-1]:
                for x in path:
                    print('chdir ..')
                    self.chdir('..')

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

    parser.add_argument('action', type=lambda s: s.lower(), help='Action to execute, try "help"')
    parser.add_argument('path', nargs='?', help='target used for some actions')
    parser.add_argument('-v', '--verbose', action='store_true', help='show more diagnostic messages')
    parser.add_argument('--defaults', action='store_true', help='do not read ini file, use default settings')
    # parser.add_argument('--noexp', action='store_true', help='skip steps involving the expansion board and SD storage')

    args = parser.parse_args()
    #~ print(args)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.action == 'write-ini':
        with open('wipy-ftp.ini', 'w') as f:
            f.write(INI_TEMPLATE)
        logging.info('"wipy-ftp.ini" written')
        sys.exit(0)

    if not os.path.exists('wipy-ftp.ini'):
        logging.warning('"wipy-ftp.ini" not found, using defaults')

    with WiPyActions(not args.defaults) as wipy:
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
        elif args.action == 'fwupgrade':
            print('upload /flash/sys/mcuimg.bin')
            wipy.put('/flash/sys/mcuimg.bin', open('mcuimg.bin', 'rb'))
            print('press reset button on WiPy to complete upgrade')
        else:
            sys.stdout.write(__doc__)
        # option to set ssid/pw in wificonfig.txt

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
