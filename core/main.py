import config
import sys
import threading
import time

from g4 import G4
from usb import USB

config.logging.info(sys.version_info)

if config.console_only == 'True':
    while True:
        time.sleep(1800)
        config.logging.warning("No app running, console only")
else:
    config.logging.info(' ----> Main App Running! <---- ')
    # launch USB Drive scanning and file backup process
    usb_storage = USB()
    scan_and_backup = threading.Thread(target=usb_storage.check_for_devices)
    scan_and_backup.daemon = True
    scan_and_backup.start()

    # launch polling to serial device
    serial_g4_device = G4()
    polling = threading.Thread(target=serial_g4_device.serial_polling, args=[100])
    polling.daemon = True
    polling.start()

    while True:
        pass
