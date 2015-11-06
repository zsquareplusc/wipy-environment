"""\
WLAN autoconfiguration

- try to connect to a configured AP (as STA)
- fall back to AP mode
"""
from network import WLAN
import time

def wlan():
    """Connect in STA mode, fallback to AP"""
    try:
        import wlanconfig
    except ImportError:
        print('WLAN: no wlanconfig.py')
        wlanconfig = None
        wlan = WLAN(mode=WLAN.AP)
    except Exception as e:
        print('WLAN: error in wlanconfig.py: {}'.format(e))
        wlanconfig = None
        wlan = WLAN(mode=WLAN.AP)
    else:
        try:
            # configure the WLAN subsystem in station mode (the default is AP)
            wlan = WLAN(mode=WLAN.STA)
            print('WLAN: connecting to network (AP)...')
            wlan.connect(wlanconfig.ssid, auth=(WLAN.WPA2, wlanconfig.password), timeout=5000)
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
            wlanconfig = None
        except Exception as e:
            print('WLAN: error: {}'.format(e))
            wlanconfig = None
    if wlanconfig is None:
        wlan.init(mode=WLAN.AP, ssid='wipy-wlan', auth=(WLAN.WPA2,'www.wipy.io'), channel=7, antenna=WLAN.INT_ANT)


