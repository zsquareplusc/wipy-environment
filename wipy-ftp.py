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
import shutil
import sys

INI_TEMPLATE = """\
[FTP]
server = 192.168.1.1
user = micro
pass = python
"""


class WiPySimulator(object):
    def __init__(self, root_directory):
        self.root = os.path.abspath(root_directory)
        self.log = logging.getLogger('FTP')
        self.log.debug('WiPy FTP Simulator in {}'.format(self.root))
        if not os.path.exists(os.path.join(self.root, 'flash')):
            os.mkdir(os.path.join(self.root, 'flash'))
            os.mkdir(os.path.join(self.root, 'flash', 'lib'))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def ls(self, path=None):
        """List files, meant for interactive use"""
        if path is None:
            path = '/'
        print(os.listdir(os.path.join(self.root, path)))

    def makedirs(self, dirname):
        """Recursively create directories, if not yet existing"""
        self.log.info('makedirs {}'.format(dirname))
        os.makedirs(os.path.join(self.root, os.path.relpath(dirname, '/')), exist_ok=True)

    def put(self, filename, fileobj):
        """send binary file"""
        self.log.info('put {}'.format(filename))
        with open(os.path.join(self.root, os.path.relpath(filename, '/')), 'wb') as dst:
            shutil.copyfileobj(fileobj, dst)

    def get(self, filename, fileobj):
        """receive binary file"""
        self.log.info('get {}'.format(filename))
        with open(os.path.join(self.root, os.path.relpath(filename, '/')), 'rb') as src:
            shutil.copyfileobj(src, fileobj)

    def cat(self, filename, write_function):
        """Pipe (text) file contents to stdout, meant for interactive use"""
        self.log.debug('cat {}'.format(filename))
        for line in open(os.path.join(self.root, os.path.relpath(filename, '/'))):
            write_function(line.rstrip())


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

    def makedirs(self, dirname):
        """Recursively create directories, if not yet existing"""
        self.log.info('makedirs {}'.format(dirname))
        self.ftp.cwd('/')
        for directory in dirname.split('/'):
            try:
                self.ftp.cwd(directory)
            except ftplib.error_perm:
                self.ftp.mkd(directory)
                self.ftp.cwd(directory)

    def put(self, filename, fileobj):
        """send binary file"""
        try:
            self.log.info('put {}'.format(filename))
            self.ftp.storbinary("STOR " + filename, fileobj, 1024)
        except ftplib.error_perm as e:
            self.log.error('invalid path: {} ({})'.format(filename, e))
        except ftplib.all_errors as e:
            self.log.error('FTP error: {}'.format(e))

    def get(self, filename, fileobj):
        """receive binary file"""
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
ssid = {ssid!r}
password = {password!r}
"""

class WiPyActions(WiPyFTP):

    def __init__(self, target):
        self.target = target

    def __enter__(self):
        self.target.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self.target.__exit__()
        pass

    def install_lib(self):
        """recursively copy /flash/lib"""
        base_path = 'device/flash/lib'
        for root, dirs, files in os.walk(base_path):
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            self.target.makedirs('/{}'.format(os.path.relpath(root, 'device')))
            for filename in files:
                remote_name = os.path.relpath(os.path.join(root, filename), 'device')
                with open(os.path.join(root, filename), 'rb') as src:
                    self.target.put('/{}'.format(remote_name), src)

    def install_top(self):
        """copy *.py in /flash"""
        for filename in glob.glob('device/flash/*.py'):
            with open(filename, 'rb') as src:
                self.target.put('/flash/{}'.format(os.path.basename(filename)), src)

    def config_wlan(self):
        ssid = input('Enter SSID: ')
        password = input('Enter passphrase: ')
        self.target.put('/flash/wlanconfig.py',
                        io.BytesIO(WLANCONFIG_TEMPLATE.format(ssid=ssid, password=password).encode('utf-8')))

def main():
    import argparse

    parser = argparse.ArgumentParser(description='WiPy copy tool')

    parser.add_argument('action', type=lambda s: s.lower(), help='Action to execute, try "help"')
    parser.add_argument('path', nargs='?', help='target used for some actions')
    parser.add_argument('-v', '--verbose', action='store_true', help='show more diagnostic messages')
    parser.add_argument('--defaults', action='store_true', help='do not read ini file, use default settings')
    parser.add_argument('--simulate', metavar='DESTDIR', help='do not access WiPy, put files in gived directory instead')
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

    if args.simulate:
        target = WiPySimulator(args.simulate)
    else:
        target = WiPyFTP(not args.defaults)
    with WiPyActions(target) as wipy:
        if args.action == 'ls':
            wipy.ls(args.path)
        elif args.action == 'sync-lib':
            wipy.install_lib()
        elif args.action == 'sync-top':
            wipy.install_top()
        elif args.action == 'install':
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
        elif args.action == 'interact':
            import code
            try:
                import rlcompleter
                import readline
            except ImportError as e:
                logging.warning('readline support failed: {}'.format(e))
            else:
                readline.set_completer(rlcompleter.Completer(locals()).complete)
                readline.parse_and_bind("tab: complete")
            code.interact(local=locals())
        else:
            sys.stdout.write(__doc__)
        # option to set ssid/pw in wificonfig.txt

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
