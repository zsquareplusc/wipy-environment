#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
WLAN autoconfiguration

- try to connect to a configured AP (as STA)
- fall back to AP mode
"""
from network import WLAN
import time
import ulog


def wlan():
    """Connect in STA mode, fallback to AP"""
    log = ulog.Logger('WLAN: ')
    try:
        import wlanconfig
    except ImportError:
        log.notice('no wlanconfig.py')
        wlanconfig = None
        wlan = WLAN(mode=WLAN.AP)
    except Exception as e:
        log.error('error in wlanconfig.py: {}'.format(e))
        wlanconfig = None
        wlan = WLAN(mode=WLAN.AP)
    else:
        try:
            # configure the WLAN subsystem in station mode (the default is AP)
            wlan = WLAN(mode=WLAN.STA)
            log.info('connecting to network (AP)...')
            wlan.connect(wlanconfig.ssid, auth=(WLAN.WPA2, wlanconfig.password), timeout=5000)
            log.info('waiting for IP...')
            for tries in range(50):
                if wlan.isconnected():
                    log.notice('''connected!
      WiPy IP: {}
      NETMASK: {}
      GATEWAY: {}
      DNS:     {}'''.format(*wlan.ifconfig()))
                    break
                time.sleep_ms(100)
        except OSError:
            log.error('found no router, going into AP mode instead')
            wlanconfig = None
        except Exception as e:
            log.error('error: {}'.format(e))
            wlanconfig = None
    if wlanconfig is None:
        wlan.init(mode=WLAN.AP, ssid='wipy-wlan', auth=(WLAN.WPA2,'www.wipy.io'), channel=7, antenna=WLAN.INT_ANT)


