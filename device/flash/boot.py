#! /usr/bin/env python3
# encoding: utf-8
#
# boot.py -- run on boot-up
# can run arbitrary Python, but best to keep it minimal
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import expansionboard
expansionboard.enable_console_on_serial()

