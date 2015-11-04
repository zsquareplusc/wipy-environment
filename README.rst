==================
 wipy environment
==================

Overview
========
Some code for the wipy_ board, facilitating setup network and running code from
the SD card.


Features
========
Assuming the ExpansionBoard_ is present.

- activate REPL on serial port
- try to connect to home network (in STA mode), fall back to AP mode if that fails.
- mount the SD card to ``/sd``
- add ``/sd/lib`` to ``sys.path`` and execute ``/sd/main.py`` on SD card


Installation
============
Copy the contents of ``device/flash`` to the wipy internal flash memory. The
contents of ``device/sd`` goes onto the SD card.

Edit ``flash/wificonfig.txt`` to contain your own AP and password (changes to
the security/WPA mode have to be made in ``main.py``)

The ``wipy-ftp.py`` can be used to upload the files.

References
==========

- wipy_ (homepage)
- `wipy manual`_

.. _wipy: http://www.wipy.io
.. _ExpansionBoard: https://github.com/wipy/wipy/tree/master/hardware/ExpansionBoard-v1.2
.. _`wipy manual`: https://micropython.org/resources/docs/en/latest/wipy/


WiPy Pins::

    .               _______________
                   | HB        RST |
    SAFEBOOT  GP28 |               | GP3
              GP22 |               | GP4
    S1        GP17 |               | GP0
    LED       GP16 |               | GP3   VBATT
    SD_DAT0   GP15 |               | GP31
              GP14 |               | GP30
              GP13 |               | GP6   FT_CTS
              GP12 |               | GP7   FT_RTS
    SD_CMD    GP11 |               | GP8
              GP24 |               | GP9
              GP23 |               | GP10  SD_CLK
    FT_TXD     GP1 |               | +3V3
    FT_RXD     GP2 |               | GND
             RESET |               | Vin
                    \    #####    /
                     \   #####   /
                      \  #####  /
                       ---------

