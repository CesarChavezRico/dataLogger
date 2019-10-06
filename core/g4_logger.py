import config
import pendulum
import serial
import time
from gpiozero import LED

from pathlib import Path


class G4:
    port = None
    g4_date_time = None

    blue_led = None
    local_running_file_lock = None

    def __init__(self, file_lock):

        self.local_running_file_lock = file_lock

        try:
            self.port = serial.Serial("/dev/ttyUSB0", baudrate=19200, timeout=1)
        except Exception as e:
            config.logging.error(f'Error Opening Serial Port (Init): {e.__str__()}')

        # Init LEDs
        self.blue_led = LED(22)

    def __get_command(self, command):
        """
        Sends and returns the result of a G4 command
        :param command: command to send, without address or CR
        :return: response from ESC. can be timeout.
        """

        # Added try/except if usb cable not connected to 222 (MCR)
        try:
            address = 1
            self.port.flushInput()
            self.port.flushOutput()
            self.port.flush()

            to_send = "{:02d}{}\x0D".format(address, command)
            self.port.write(to_send.encode())
            config.logging.debug(('g4_logger: __get_command - Tx: {0}'.format(to_send)))

            rx = self.port.readline().decode()

            if rx == '':
                config.logging.debug('g4_logger: __get_command - Timeout!')
                return "Timeout"
            elif rx[2] == command[0]:
                to_return = rx[:-2]
                config.logging.debug(('g4_logger: __get_command - Success Rx: {0}'.format(to_return)))
                return to_return
            else:
                config.logging.warning(('g4_logger: __get_command - Ugly trash! = {0}'.format(rx)))
        except Exception as e:
            try:
                try:
                    self.port.close()
                except TypeError as e:
                    config.logging.warning("NoneType: Port never initialized correctly")
                    pass
                time.sleep(1)
                self.port = serial.Serial("/dev/ttyUSB0", baudrate=19200, timeout=1)
                config.logging.warning("Serial Reconnected!")
            except Exception as e:
                config.logging.error(f'Error Opening Serial Port: {e.__str__()}')
                time.sleep(5)

    def _write_to_file(self, path, row_to_write):
        # Do we need a new file?
        file_today = Path('{0}/log_{1}.csv'.format(path, self.g4_date_time.format('YYYY-MM-DD')))
        if file_today.is_file():
            # The file exists .. append
            with open(file_today, 'a') as current_file:
                current_file.write('{0}\n'.format(row_to_write))
        else:
            # The file does not exists .. create with header then append
            header = 'timestamp,'
            for variable in config.variables:
                header += '{0},'.format(variable['name'])
            with open(file_today, 'w') as current_file:
                current_file.write('{0}\n'.format(header))
                current_file.write('{0}\n'.format(row_to_write))

    def serial_polling(self):
        """
        Polls G4 device in a predefined rate. Uses D(x) fot variables configuration

        """
        while True:
            try:
                mb = self.__get_command('MB')
                time.sleep(.1)
                config.logging.debug("Response from G4 - MB: [{0}]".format(mb))

                s_1 = self.__get_command('S?1')
                time.sleep(.1)
                config.logging.debug("Response from G4 - S?1: [{0}]".format(s_1))

                e = self.__get_command('E')
                time.sleep(.1)
                config.logging.debug("Response from G4 - E: [{0}]".format(e))

                h = self.__get_command('H')
                time.sleep(.1)
                config.logging.debug("Response from G4 - H: [{0}]".format(h))

                row_to_write = None
                try:
                    self.g4_date_time = pendulum.from_format(h[3:], 'HH:mm:ss DD/MM/YY')
                    row_to_write = '{0},'.format(self.g4_date_time.timestamp())
                except (ValueError, TypeError):
                    config.logging.error('Error in G4 device time: {0}'.format(h))

                for variable in config.variables:
                    if variable['command'] == 'MB':
                        raw_value = int(mb[variable['base_index']:variable['base_index']+4], 16)
                        value = (raw_value * variable['m']) + variable['b']
                        row_to_write += f'{value},'
                        config.logging.debug('{0} = {1}'.format(variable['name'], value))
                    elif variable['command'] == 'E':
                        bit_value = self.get_bit_state(variable['base_index'], variable['bit_index'])
                        row_to_write += f'{bit_value},'
                        config.logging.debug('{0} = {1}'.format(variable['name'], bit_value))
                with self.local_running_file_lock:
                    # Write to Permanent USB memory LED (blue)
                    self.blue_led.on()

                    config.logging.info('row to write = {0}'.format(row_to_write))

                    # -------> Running File
                    self._write_to_file('/media/permanent_usb_storage/running', row_to_write)
                    # -------> Backup File
                    self._write_to_file('/media/permanent_usb_storage/backup', row_to_write)

                    # Write to Permanent USB memory LED (blue)
                    self.blue_led.off()

            except ValueError as e:
                config.logging.info("ValueError: {0}".format(e))
            except IOError as e:
                config.logging.info("IOError: {0}".format(e))
            except TypeError as e:
                config.logging.info("TypeError: {0}".format(e))

            time.sleep(config.rate)

    @staticmethod
    def get_bit_state(string, bit_num):
        """
        Returns the state of a bit out of a Hex string
        Usage: get_bit_state(e[16:17], 1)
        :return bit state as 1 or 0
        """
        byte = int(string, 16)
        if bit_num == 7:
            mask = 128
            if byte & mask:
                return 1
            else:
                return 0
        elif bit_num == 6:
            mask = 64
            if byte & mask:
                return 1
            else:
                return 0
        elif bit_num == 5:
            mask = 32
            if byte & mask:
                return 1
            else:
                return 0
        elif bit_num == 4:
            mask = 16
            if byte & mask:
                return 1
            else:
                return 0
        elif bit_num == 3:
            mask = 8
            if byte & mask:
                return 1
            else:
                return 0
        elif bit_num == 2:
            mask = 4
            if byte & mask:
                return 1
            else:
                return 0
        elif bit_num == 1:
            mask = 2
            if byte & mask:
                return 1
            else:
                return 0
        elif bit_num == 0:
            mask = 1
            if byte & mask:
                return 1
            else:
                return 0
        else:
            return 0

