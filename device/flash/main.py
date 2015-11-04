# main.py -- put your code here!

import expansionboard
import autoconfig

autoconfig.wlan()

print('SD: preparing SD card')
if expansionboard.initialize_sd_card():
    print('SD: mounted to /sd')
    print('SD: execute /sd/main.py...')
    try:
        execfile('/sd/main.py')
    except OSError: # XXX bad, hides other errors than file not existing
        print('SD: no file /sd/main.py found!')
else:
    print('SD: no card found!')


