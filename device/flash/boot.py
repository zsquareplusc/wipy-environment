# boot.py -- run on boot-up
# can run arbitrary Python, but best to keep it minimal

from machine import UART
import os
uart = UART(0, 115200)
os.dupterm(uart)


