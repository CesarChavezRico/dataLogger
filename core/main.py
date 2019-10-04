import config
import threading
import time

from g4_logger import G4
from usb import USB

if config.console_only == 'True':
    while True:
        time.sleep(1800)
        config.logging.warning("No app running, console only")
else:
    config.logging.info(' ----> Main App Running! <---- ')
    # Create Lock for running file in permanent USB memory
    running_file_lock = threading.Lock()

    # launch USB Drive scanning and file backup process
    usb_storage = USB(running_file_lock)
    scan_and_backup = threading.Thread(target=usb_storage.check_for_devices)
    scan_and_backup.daemon = True
    scan_and_backup.start()

    # launch polling to serial device
    serial_g4_device = G4(running_file_lock)
    polling = threading.Thread(target=serial_g4_device.serial_polling)
    polling.daemon = True
    polling.start()

    while True:
        pass
