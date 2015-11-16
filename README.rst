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

.. note::

    The default fallback to AP mode is a security risk as the netowork name and passwort
    may be known (unless they were changed in the source code here)


Installation on WiPy
====================
The ``wipy-ftp.py`` can be used to upload the files. For first time usage
(assuming the WiPy_ is in AP mode with default settings, PC connected to this
AP)::

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

Once the WiPy_ connects to a router, its IP address must be updated in
``wipy-ftp.ini``.


WiPy-FTP Tool
=============
``wipy-ftp.py`` is a tool to upload/download files via FTP.

    Usage: wipy-ftp.py [-v --defaults] ACTION [ARGS]

      -v, --verbose     print more diagnostic messages
      --defaults        ignore .ini file and use defaults

    ACTIONS are:

    - ``write-ini`` create ``wipy-ftp.ini`` with default settings
    - ``install``  copy boot.py, main.py and /lib from the PC to the WiPy
    - ``sync-lib`` copies only /lib
    - ``sync-top`` copies only boot.py, main.py
    - ``config-wlan`` ask for SSID/Password and write wlanconfig.py on WiPy
    - ``ls`` with optional path argument: list files
    - ``cat`` with filename: show text file contents
    - ``backup`` download everything in ``/flash``
    - ``fwupgrade``  write mcuimg.bin file to WiPy for firmware upgrade
    - ``help``  this text


For configuration, a file called ``wipy-ftp.ini`` must be present with the
following contents::

    [FTP]
    server = 192.168.1.1
    user = micro
    pass = python

The default file can be created by running ``wipy-ftp.py write-ini``.
These settings need to be changed, once the WiPy_ is connected to an access point.


Technical Details
=================
The contents of ``device/flash`` goes to the WiPy_ internal flash memory. The
contents of ``device/sd`` goes onto the SD card.

The WLAN configuration for STA mode are stored in ``flash/wlanconfig.py`` on
the WiPy. This file is written by the ``config-wlan`` action. The security/WPA
mode have to be changed in ``/lib/autoconfig.py``, the default is WPA2.

Actions
-------
``install``
    Designed for first time / one time usage.

``backup``
    Downloads the contents of ``/flash`` into a newly created directory. The
    diretory will be named ``backup_<date>``

``ls`` and ``cat``
    These commands write text to stdout.

``fwupgrade``
    First download the image using ``download-mcuimg.py``, which should locate
    the latest binary on github and then run this action to download the
    firmware to the WiPy_.

``sync-lib``
    Recursively copy the ``device/lib`` directory to the WiPy_. Can be used
    repeatedly to download updates to the library.


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

