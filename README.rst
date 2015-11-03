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
- mount the SD card
- execute ``main.py`` on SD card


Installation
============
Copy the contents of ``device/flash`` to the wipy internal flash memory. The
contents of ``device/sd`` goes onto the SD card.

Edit ``flash/wificonfig.txt`` to contain your own AP and password (changes to
the security/WPA mode have to be made in ``main.py``)


References
==========

- wipy_ (homepage)
- `wipy manual`_

.. _wipy: http://www.wipy.io
.. _ExpansionBoard: https://github.com/wipy/wipy/tree/master/hardware/ExpansionBoard-v1.2
.. _`wipy manual`: https://micropython.org/resources/docs/en/latest/wipy/
