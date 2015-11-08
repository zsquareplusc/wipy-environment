# main.py -- put your code here!

import expansionboard
import autoconfig
import upathlib

autoconfig.wlan()

print('SD: preparing SD card')
if expansionboard.initialize_sd_card():
    main = upathlib.Path('/sd/main.py')
    print('SD: mounted to /sd')
    print('SD: execute {}...'.format(main))
    if main.exists():
        execfile(str(main))
    else:
        print('SD: no file /sd/main.py found!')
else:
    print('SD: no card found!')


