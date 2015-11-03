# main.py -- put your code here!

import machine
from machine import SD
from network import WLAN
import time
import os

with open('/flash/wificonfig.txt') as f:
    ssid = f.readline().strip()
    passwd = f.readline().strip()

# configure the WLAN subsystem in station mode (the default is AP)
print('Wait up to 5s for WLAN...')
wlan = WLAN(mode=WLAN.STA)
try:
    wlan.connect(ssid, auth=(WLAN.WPA2, passwd), timeout=5000)
    print('waiting for IP...')
    for tries in range(50):
        if wlan.isconnected():
            print('WLAN connected to router:', wlan.ifconfig())
            break
        time.sleep_ms(100)
except OSError:
    print('WLAN found no router, going into AP mode instead')
    wlan.init(mode=WLAN.AP, ssid='wipy-wlan', auth=(WLAN.WPA2,'www.wipy.io'), channel=7, antenna=WLAN.INT_ANT)

print('Preparing /sd')
try:
    # clock pin, cmd pin, data0 pin
    sd = SD(pins=('GP10', 'GP11', 'GP15'))
    # or use default ones for the expansion board
    sd = SD()
    os.mount(sd, '/sd')
except OSError:
    print('no SD card found!')
else:
    print('Execute /sd/main.py...')
    try:
        execfile('/sd/main.py')
    except OSError:
        print('no file /sd/main.py found!')


