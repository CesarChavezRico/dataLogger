
import sys
import threading

from g4 import G4
from usb import USB

print(sys.version_info)

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
