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
import ulog

autoconfig.wlan()

# XXX ulog remote config

if expansionboard.initialize_sd_card():
    main = upathlib.Path('/sd/main.py')
    ulog.root.info('execute {}...'.format(main))
    if main.exists():
        execfile(str(main))
    else:
        ulog.root.warn('no file /sd/main.py found!')


