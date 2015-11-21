#! /usr/bin/env python3
# encoding: utf-8
#
# main.py -- put your code here!
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import expansionboard
import autoconfig
import upathlib

autoconfig.wlan()

print('SD: preparing SD card')
if expansionboard.initialize_sd_card():
    main = upathlib.Path('/sd/main.py')
    print('SD: mounted to /sd')
    print('SD: execute {}...'.format(main))
    if main.exists():
        execfile(str(main))
    else:
        print('SD: no file /sd/main.py found!')
else:
    print('SD: no card found!')


