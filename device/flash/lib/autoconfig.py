"""\
WLAN autoconfiguration

- try to connect to a configured AP (as STA)
- fall back to AP mode
"""
from network import WLAN
import time

def wlan():
    with open('/flash/wificonfig.txt') as f:
        ssid = f.readline().strip()
        passwd = f.readline().strip()

    # configure the WLAN subsystem in station mode (the default is AP)
    print('WLAN: connecting to network (AP)...')
    wlan = WLAN(mode=WLAN.STA)
    try:
        wlan.connect(ssid, auth=(WLAN.WPA2, passwd), timeout=5000)
        print('WLAN: waiting for IP...')
        for tries in range(50):
            if wlan.isconnected():
                print('''\
WLAN: connected!
      WiPy IP: {}
      NETMASK: {}
      GATEWAY: {}
      DNS:     {}'''.format(*wlan.ifconfig()))
                break
            time.sleep_ms(100)
    except OSError:
        print('WLAN: found no router, going into AP mode instead')
        wlan.init(mode=WLAN.AP, ssid='wipy-wlan', auth=(WLAN.WPA2,'www.wipy.io'), channel=7, antenna=WLAN.INT_ANT)


