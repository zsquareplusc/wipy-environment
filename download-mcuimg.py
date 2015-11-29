#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
WiPy Download Tool (Download site -> PC)

Downloads WiPy firmware image to PC ("mcuimg.bin")
that can then be used to upgrade the WiPy (e.g. using an FTP
client or with "wipy-ftp.py fwupgrade")

The fw source can be selected from
- github.com/wipy/wipy/releases/download , official releases (default)
- www.micropython.org/downloads , daily builds (--latest)

Usage: download-mcuimg.py [-v] [--latest]

-v, --verbose     print more diagnostic messages
--latest          download from micropython.org/download for latest builds

"""

import urllib.request
from pprint import pprint
import zipfile
import json

def main():
    import argparse
    import logging

    parser = argparse.ArgumentParser(description='WiPy FW download tool')
    parser.add_argument('-v', '--verbose', action='store_true', help='show more diagnostic messages')
    parser.add_argument('--latest', action='store_true', help='download latest (inofficial) builds from micropython.org/downloads')
    args = parser.parse_args()
    #~ print(args)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.latest:
        logging.debug('downloading bleeding edge builds from http://micropython.org/downloads')
        html_site = urllib.request.urlopen('http://micropython.org/download').read().decode('utf-8')
        hit_index_start = html_site.find('http://micropython.org/resources/firmware/wipy-')
        if hit_index_start:
            snippset = html_site[hit_index_start:hit_index_start+150]
        else:
            logging.error("did not find fitting fw image on server")
            return
        # XXX a bit hacky
        zip_url = snippset[:snippset.find("zip")+3]
    else:
        logging.debug('downloading latest official release')
        release_info = json.loads(urllib.request.urlopen('https://api.github.com/repos/wipy/wipy/releases/latest').read().decode('utf-8'))
        logging.info("TAG: {}, NAME: {}".format(release_info['name'],release_info['tag_name']))
        zip_url = release_info['assets'][0]['browser_download_url']

    logging.debug('Downloading ZIP from: {}'.format(zip_url))
    with open('Binaries.zip', 'wb') as f:
        f.write(urllib.request.urlopen(zip_url).read())

    logging.info('Extracting mcuimg.bin...')
    with zipfile.ZipFile('Binaries.zip', 'r') as archive:
        # logging.info('{}'.format(archive.printdir()))
        for filename in archive.namelist():
            if filename.find('mcuimg') != -1:
                with open('mcuimg.bin', 'wb') as f:
                    f.write(archive.open(filename).read())

    logging.info('downloaded mcuimg.bin successully')
    logging.info('proceed now with "wipy-ftp.py fwupgrade" to update your WiPy')



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
