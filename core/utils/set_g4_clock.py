import pendulum
import serial


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
        to_return = rx[:-2]
        print(('g4_esc_petrolog: __get_command - Success Rx: {0}'.format(to_return)))
        return to_return
    else:
        print(('g4_esc_petrolog: __get_command - Ugly trash! = {0}'.format(rx)))


g4_clock = pendulum.now()
g4_clock_to_send = g4_clock.format('HH mm ss DD MM YY ')
__get_command('SH{0}'.format(g4_clock_to_send))

