#! /usr/bin/env python3

import urllib.request
from pprint import pprint
import zipfile
import json

print('Downloading release info..')
release_info = json.loads(urllib.request.urlopen('https://api.github.com/repos/wipy/wipy/releases/latest').read().decode('utf-8'))
with open('mcuimg.txt', 'w') as f:
    pprint(release_info, f)

print('TAG: {}'.format(release_info['tag_name']))
print('NAME: {}'.format(release_info['name']))

zip_url = release_info['assets'][0]['browser_download_url']

print('Downloading ZIP from: {}'.format(zip_url))
with open('Binaries.zip', 'wb') as f:
    f.write(urllib.request.urlopen(zip_url).read())

print('Extracting mcuimg.bin...')
with zipfile.ZipFile('Binaries.zip', 'r') as archive:
    with open('mcuimg.bin', 'wb') as f:
        f.write(archive.open('mcuimg.bin').read())

print('perform firmware upgrade with "wipy-ftp.py fwupgrade"...')
