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
- libraies for the WiPy_:

  - ``ulog``
  - ``upathlib``

PC tools:

- a tool to sync files from the PC with the WiPy_ (via FTP). It can also send
  the firmware file or backup the WiPy_ internal flash.
- an other tool to download firmware images from the internet

.. note::

    The default fallback to AP mode is a security risk as the network name and password
    may be known (unless they were changed in the source code here)


Installation on WiPy
====================
The ``wipy-ftp.py`` tool can be used to upload the files. For first time usage
(assuming the WiPy_ is in AP mode with default settings, PC connected to this
AP)::

    $ python3 wipy-ftp.py install
    INFO:root:using ftp
    INFO:root:backing up /flash into backup_2015-11-22_12_12_12
    INFO:FTP:get /flash/main.py
    INFO:FTP:get /flash/boot.py
    INFO:FTP:put /flash/boot.py
    INFO:FTP:put /flash/main.py
    INFO:FTP:makedirs /flash/lib
    INFO:FTP:put /flash/lib/expansionboard.py
    INFO:FTP:put /flash/lib/upathlib.py
    INFO:FTP:put /flash/lib/autoconfig.py
    Connect to an access point? [Y/n]: y
    Enter SSID: <your SSID>
    Enter passphrase: <your password>

The original contents of ``/flash`` is backed up in a subdirectory.


WiPy-FTP Tool
=============
``wipy-ftp.py`` is a tool to upload/download files via FTP.

    usage: wipy-ftp.py [-h] [-v] [--defaults] [--simulate DESTDIR]
                       action [path] [destination]

    WiPy copy tool

    positional arguments:
      action          Action to execute, try "help"
      path            pathname used for some actions
      destination     target used for some actions

    optional arguments:
      -h, --help      show this help message and exit
      -v, --verbose   show more diagnostic messages
      --defaults      do not read ini file, use default settings
      --ini INI       alternate name for settings file (default: wipy-ftp.ini)
      --simulate DIR  do not access WiPy, put files in given directory instead

    For configuration, a file called ``wipy-ftp.ini`` should be present. Run
    "wipy-ftp.py write-ini" to create one. Adapt as needed when connected via
    router.


Actions
-------

``install``
    Designed for first time / one time usage. It corresponds to running the
    action ``backup``, ``sync-top``, ``sync-lib`` and ``config-wlan``.

``backup``
    Downloads the contents of ``/flash`` into a newly created directory. The
    directory will be named ``backup_<date>``

``ls [path]``
    List directory (on stdout).

``cat path``
    Retrieve ``path`` and write it to stdout (binary).

``cp local_src remote_dst``
    Copy a single file from PC to device.

``fwupgrade``
    Write ``mcuimg.bin`` file to WiPy for firmware upgrade. First download the
    image using ``download-mcuimg.py`` and then run this action to download the
    firmware to the WiPy_.

``sync-lib``
    Recursively copy the ``device/lib`` directory to the WiPy_. Can be used
    repeatedly to download updates to the library.

``sync-top``
    Copies ``boot.py``, ``main.py`` to the device.

``write-ini``
    Create ``wipy-ftp.ini`` with default settings.

``config-wlan``
    Ask for SSID/Password and write ``wlanconfig.py`` on WiPy_.

``config-ulog``
    Ask for host/port settings for remote logging using ulog, writes
    ``ulogconfig.py`` on WiPy_.


Configuration
-------------
For configuration, a file called ``wipy-ftp.ini`` should be present with the
following contents::

    [FTP]
    server = 192.168.1.1
    user = micro
    pass = python

The default file can be created by running ``wipy-ftp.py write-ini``.  These
settings need to be changed, once the WiPy_ is connected to an access point.

The option ``--ini`` can be used to choose a different filename for the ini
file, which may be helpful when working with multiple boards.


Download Tool
=============
The ``download-mcuimg.py`` tool downloads the firmware archive and extracts
``mcuimg.bin``. It will search for the latest release on github, unless
``--latest`` is given, then it downloads the latest (inofficial) build from
micropython.org/downloads.

    usage: download-mcuimg.py [-h] [-v] [--latest]

    WiPy FW download tool

    optional arguments:
      -h, --help     show this help message and exit
      -v, --verbose  show more diagnostic messages
      --latest       download latest (inofficial) builds from
                     micropython.org/downloads


Technical Details
=================
The contents of ``device/flash`` goes to the WiPy_ internal flash memory. The
contents of ``device/sd`` goes onto the SD card.

The WLAN configuration for STA mode are stored in ``flash/wlanconfig.py`` on
the WiPy_. This file is written by the ``config-wlan`` action. The security/WPA
mode has to be changed in ``/lib/autoconfig.py``, the default is WPA2.

The ``--simulation`` can be used to for testing. The option needs to point to an
existing local directory. All FTP operations are then simulated using files in
that location.


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

