import config
import pendulum
import serial
import time


class G4:
    port = None
    g4_date_time = None

    def __init__(self):
        self.port = serial.Serial("/dev/ttyUSB0", baudrate=19200, timeout=1)

    def __get_command(self, command):
        """
        Sends and returns the result of a G4 command
        :param command: command to send, without address or CR
        :return: response from ESC. can be timeout.
        """
        address = 1
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()

        to_send = "{:02d}{}\x0D".format(address, command)
        self.port.write(to_send.encode())
        config.logging.debug(('g4_esc_petrolog: __get_command - Tx: {0}'.format(to_send)))

        rx = self.port.readline().decode()
        if rx == '':
            config.logging.debug('g4_esc_petrolog: __get_command - Timeout!')
            return "Timeout"
        elif rx[2] == command[0]:
            to_return = rx[:-2]
            config.logging.debug(('g4_esc_petrolog: __get_command - Success Rx: {0}'.format(to_return)))
            return to_return
        else:
            config.logging.warning(('g4_esc_petrolog: __get_command - Ugly trash! = {0}'.format(rx)))

    def serial_polling(self, rate):
        """
        Polls G4 device in a predefined rate. Uses D(x) fot variables configuration
        :param rate: polling frequency in seconds
        """
        while True:
            try:
                h = self.__get_command('H')
                time.sleep(.1)
                config.logging.info("Response from G4 - H: [{0}]".format(h))
                try:
                    self.g4_date_time = pendulum.from_format(h[3:], 'HH:mm:ss DD/MM/YY')
                except ValueError:
                    config.logging.error('Error in G4 device time: {0}'.format(h))

                mb = self.__get_command('MB')
                time.sleep(.1)
                config.logging.info("Response from G4 - MB: [{0}]".format(mb))

                s_1 = self.__get_command('S?1')
                time.sleep(.1)
                config.logging.info("Response from G4 - S?1: [{0}]".format(s_1))

                e = self.__get_command('E')
                time.sleep(.1)
                config.logging.info("Response from G4 - E: [{0}]".format(e))

                for variable in config.variables:
                    if variable['command'] == 'MB':
                        raw_value = int(mb[variable['base_index']:variable['base_index']+4], 16)
                        value = (raw_value * variable['m']) + variable['b']
                        config.logging.info('{0} = {1}'.format(variable['name'], value))
                    elif variable['command'] == 'E':
                        # TODO: Add implementation for boolean values (will require function 'get_bit_state')
                        pass

            except ValueError as e:
                config.logging.info("ValueError: {0}".format(e))
            except IOError as e:
                config.logging.info("IOError: {0}".format(e))
            time.sleep(rate)
