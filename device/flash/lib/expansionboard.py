#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Functions related to the ExpansionBoard
https://github.com/wipy/wipy/tree/master/hardware/ExpansionBoard-v1.2
"""
from machine import Pin
from machine import SD
from machine import UART
import ulog
import os
import sys

sd = None
uart = None

# initialize GPIO16 (GN LED on expansion board) in gpio mode (alt=0) and make it an output
led = Pin('GP16', mode=Pin.OUT)
led(1) # LED OFF

s1 = Pin('GP17', mode=Pin.IN, pull=Pin.PULL_UP)

# XXX Vbatt analog input: GP3


def initialize_sd_card():
    """Try to mount SD card and append /sd/lib to sys.path"""
    global sd
    log = ulog.Logger('SD: ')
    try:
        log.info('preparing SD card')
        sd = SD(pins=('GP10', 'GP11', 'GP15'))
        os.mount(sd, '/sd')
        sys.path.append('/sd/lib')
    except OSError:
        log.info('no card found!')
        return False
    else:
        log.info('mounted to /sd')
        return True


def enable_console_on_serial():
    """Enable REPL on USB serial connection"""
    global uart
    uart = UART(0, 115200)
    os.dupterm(uart)


def set_callback_for_switch(callback):
    """Set a function to be run when the button is pressed"""
    if callback is not None:
        s1.irq(trigger=Pin.IRQ_FALLING, priority=1, handler=callback)
    else:
        s1.irq(trigger=0)

