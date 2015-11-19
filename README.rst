==================
 wipy environment
==================

Overview
========
Some code for the WiPy_ board, facilitating setup network and running code from
the SD card.

Code for the PC simplifies first time setup and later copying data to the WiPy_
or backing it up.

Features
========
Assuming the ExpansionBoard_ (or a similar setup) is present.

- activate REPL on serial port
- try to connect to home network (in STA mode), fall back to AP mode if that fails.
- try to mount the SD card to ``/sd``
- add ``/sd/lib`` to ``sys.path`` and execute ``/sd/main.py`` on SD card

Pc tools:

- a tool to sync files from the PC with the WiPy_ (via FTP). It can also send
  the firmware file or backup the WiPy_ internal flash.
- an other tool to download firmware images from the internet

.. note::

    The default fallback to AP mode is a security risk as the network name and password
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

    usage: wipy-ftp.py [-h] [-v] [--defaults] [--simulate DESTDIR]
                       action [path] [destination]

    WiPy copy tool

    positional arguments:
      action              Action to execute, try "help"
      path                pathname used for some actions
      destination         target used for some actions

    optional arguments:
      -h, --help          show this help message and exit
      -v, --verbose       show more diagnostic messages
      --defaults          do not read ini file, use default settings
      --simulate DESTDIR  do not access WiPy, put files in given directory instead

    For configuration, a file called ``wipy-ftp.ini`` should be present. Run
    "wipy-ftp.py write-ini" to create one. Adapt as needed when connected via
    router.


ACTIONS are:

- ``write-ini`` create ``wipy-ftp.ini`` with default settings
- ``install``  copy ``boot.py``, ``main.py`` and ``/lib`` from the PC to the WiPy_
- ``sync-lib`` recursively copies ``/lib``
- ``sync-top`` copies ``boot.py``, ``main.py``
- ``config-wlan`` ask for SSID/Password and write ``wlanconfig.py`` on WiPy_
- ``ls`` with optional path argument: list files
- ``cat`` with filename: show text file contents
- ``backup`` download everything in ``/flash``
- ``fwupgrade``  write ``mcuimg.bin`` file to WiPy for firmware upgrade


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
the WiPy_. This file is written by the ``config-wlan`` action. The security/WPA
mode have to be changed in ``/lib/autoconfig.py``, the default is WPA2.

Actions
-------
``install``
    Designed for first time / one time usage. It corresponds to running the
    action ``backup``, ``sync-top``, ``sync-lib`` and ``config-wlan``.

``backup``
    Downloads the contents of ``/flash`` into a newly created directory. The
    directory will be named ``backup_<date>``

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

- http://www.wipy.io
- WiPy_ (github)
- `WiPy manual`_

.. _WiPy: https://github.com/wipy/wipy
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

