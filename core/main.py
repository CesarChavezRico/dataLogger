
import sys
import serial
import time

import pyudev


print(sys.version_info)
port = serial.Serial("/dev/ttyUSB0", baudrate=19200, timeout=1)


def __get_command(command):
    """
    Sends and returns the result of a G4 command
    :param command: command to send, without address or CR
    :return: response from ESC. can be timeout.
    """
    address = 1
    port.flushInput()
    port.flushOutput()
    port.flush()

    to_send = "{:02d}{}\x0D".format(address, command)
    port.write(to_send.encode())
    print(('g4_esc_petrolog: __get_command - Tx: {0}'.format(to_send)))

    rx = port.readline().decode()
    if rx == '':
        print('g4_esc_petrolog: __get_command - Timeout!')
        return "Timeout"
    elif rx[2] == command[0]:
        to_return = rx[:-1]
        print(('g4_esc_petrolog: __get_command - Success Rx: {0}'.format(to_return)))
        return to_return
    else:
        print(('g4_esc_petrolog: __get_command - Ugly trash! = {0}'.format(rx)))


context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
# For USB devices
monitor.filter_by('usb')
for action, device in monitor:
    vendor_id = device.get('ID_VENDOR_ID')
    print('{0}: {1}'.format(action, device))

while True:
    try:
        mb = __get_command('MB')
        time.sleep(.1)
        print("Response from G4 - MB: [{0}]".format(mb))

        mb = __get_command('S?1')
        time.sleep(.1)
        print("Response from G4 - S?1: [{0}]".format(mb))

        mb = __get_command('H')
        time.sleep(.1)
        print("Response from G4 - H: [{0}]".format(mb))

    except ValueError as e:
        print("ValueError: {0}".format(e))
    except IOError as e:
        print("IOError: {0}".format(e))
    time.sleep(2)
