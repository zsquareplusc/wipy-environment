==================
 wipy environment
==================

Overview
========
Some code for the WiPy_ board, facilitating setup network and running code from
the SD card.


Features
========
Assuming the ExpansionBoard_ is present.

- activate REPL on serial port
- try to connect to home network (in STA mode), fall back to AP mode if that fails.
- mount the SD card to ``/sd``
- add ``/sd/lib`` to ``sys.path`` and execute ``/sd/main.py`` on SD card
- a tool to sync files from the PC with the WiPy_ (via FTP)

.. notice::

    The default fallback to AP mode is a security risk as the netowork name and passwort
    may be known (unless they were changed in the source code here)


Installation
============
Copy the contents of ``device/flash`` to the WiPy_ internal flash memory. The
contents of ``device/sd`` goes onto the SD card.

Edit ``flash/wificonfig.txt`` to contain your own AP and password (changes to
the security/WPA mode have to be made in ``main.py``)

The ``wipy-ftp.py`` can be used to upload the files. For first time usage::

    python3 wipy-ftp.py install
    INFO:FTP:put /flash/boot.py
    INFO:FTP:put /flash/main.py
    INFO:FTP:put /flash/lib/expansionboard.py
    INFO:FTP:put /flash/lib/autoconfig.py
    Connect to an access point? [Y/n]: y
    Enter SSID: <your SSID>
    Enter passphrase: <your password>

.. warning::

    ``wipy-ftp.py install`` Overwrites files without asking. Backup The files
    before running this tool when the WiPy_ was used before.


WiPy-FTP Tool
=============
``wipy-ftp.py`` is a tool to upload/download files via FTP.

For configuration, a file called ``wipy-ftp.ini`` must be present with the
following contents::

    [FTP]
    server = 192.168.1.1
    user = micro
    pass = python

These settings need to be changed, once the WiPy_ is connected to an access point.


References
==========

- WiPy_ (homepage)
- `WiPy manual`_

.. _WiPy: http://www.wipy.io
.. _ExpansionBoard: https://github.com/wipy/wipy/tree/master/hardware/ExpansionBoard-v1.2
.. _`WiPy manual`: https://micropython.org/resources/docs/en/latest/wipy/


WiPy_ Pins::

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

