import config
from pathlib import Path
import os
import pyudev
from subprocess import call, check_output, CalledProcessError, STDOUT
from gpiozero import LED


class USB:
    monitor = None
    mount_path = '/media/usb_storage'
    permanent_mount_path = '/media/permanent_usb_storage'
    permanent_dev_name = '/dev/permanent_usb_drive'

    red_led = None
    local_running_file_lock = None

    def __init__(self, file_lock):

        self.local_running_file_lock = file_lock

        context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(context, source=u'kernel')
        call(["udevadm", "trigger"])  # Make sure that UDEV rules executed
        self._mount_usb(self.permanent_mount_path, self.permanent_dev_name)  # Mount our permanent USB drive

        try:
            check_output(['mkdir', '{0}/running'.format(self.permanent_mount_path)], stderr=STDOUT)
        except CalledProcessError as e:
            if 'File exists' in e.output.decode():
                config.logging.info(f'Known error - File exists for: {self.permanent_mount_path}/running')
            else:
                config.logging.error(f'Error creating directory in external drive: {str(e)}')

        try:
            check_output(['mkdir', '{0}/backup'.format(self.permanent_mount_path)], stderr=STDOUT)
        except CalledProcessError as e:
            if 'File exists' in e.output.decode():
                config.logging.info(f'Known error - File exists for: {self.permanent_mount_path}/backup')
            else:
                config.logging.error(f'Error creating directory in external drive: {str(e)}')

        # Init LEDs
        self.red_led = LED(23)

    @staticmethod
    def _mount_usb(mount_path, dev_name):
        try:
            check_output(['mkdir', mount_path], stderr=STDOUT)
        except CalledProcessError as e:
            if 'File exists' in e.output.decode():
                config.logging.info(f'Known error - File exists for: {mount_path}')
            else:
                config.logging.error(f'Error creating directory in external drive: {str(e)}')
        finally:
            try:
                check_output(['mount', dev_name, mount_path], stderr=STDOUT)
            except CalledProcessError as e:
                if 'USB drive' in e.output.decode():
                    config.logging.info(f'Known error - USB drive for: {dev_name}')
                else:
                    config.logging.error(f'_mount_usb: Error mounting [{dev_name}]: {str(e)}')
                    raise CalledProcessError

    def check_for_devices(self):
        devices_count = 0
        # Filter for 'Block' devices
        self.monitor.filter_by('block')
        for action, device in self.monitor:
            dev_name = device.get('DEVNAME')
            config.logging.info('{0}: {1}'.format(action, dev_name))
            if action == 'add':
                with self.local_running_file_lock:
                    self.red_led.on()
                    devices_count += 1
                    config.logging.warning('Trying to mount device #{0}: {1} ...'.format(devices_count, dev_name))

                    try:
                        self._mount_usb(self.mount_path, dev_name)
                        try:
                            check_output(['mkdir', '{0}/data_logger'.format(self.mount_path)], stderr=STDOUT)
                        except CalledProcessError as e:
                            if 'File exists' in e.output.decode():
                                config.logging.info(f'Known error - File exists for: {self.mount_path}/data_logger')
                            else:
                                config.logging.error(f'Error creating directory in external drive: {str(e)}')

                        files = os.listdir(f'{self.permanent_mount_path}/running/')
                        try:
                            for file in files:
                                destination_file = Path(f'{self.mount_path}/data_logger/{file}')
                                if destination_file.is_file():
                                    config.logging.warning(f'[external backup] [{file}] already exists in destination'
                                                           f' - Appending')
                                    with open(f'{self.permanent_mount_path}/running/{file}', 'r') as source_file:
                                        contents = source_file.readlines()
                                        with open(destination_file, 'a') as des_file:
                                            des_file.writelines(contents[1:])

                                else:
                                    config.logging.warning(f'[external backup] [{file}] not found in destination'
                                                           f' - Just copying')
                                    result = check_output(['cp',
                                                           f'{self.permanent_mount_path}/running/{file}',
                                                           f'{self.mount_path}/data_logger/{file}'], stderr=STDOUT)
                                    print(f'result from cp: \n{result}')

                                config.logging.warning(f'[external backup] deleting internal [{file}]')
                                result = check_output(['rm',
                                                       f'{self.permanent_mount_path}/running/{file}'], stderr=STDOUT)

                        except CalledProcessError as e:
                            config.logging.error(
                                f'Fatal Error backing up [{file}]: {str(e)}')
                            continue
                        try:
                            config.logging.warning('Backup completed! ... Unmounting')
                            check_output(['umount', self.mount_path], stderr=STDOUT)
                        except CalledProcessError as e:
                            output = e.output.decode()
                            config.logging.error('Fatal error unmounting device #{0}: {1}'.format(devices_count,
                                                                                                  output))
                            continue
                        try:
                            check_output(['rm', '-r', self.mount_path], stderr=STDOUT)
                        except CalledProcessError as e:
                            output = e.output.decode()
                            config.logging.error('Fatal error removing mounting directory for device #{0}: {1}'
                                                 .format(devices_count, output))
                            continue
                        self.red_led.off()

                    except CalledProcessError as e:
                        config.logging.error('check_for_devices: Fatal error mounting or copying to USB drive: '
                                             '{0}'.format(e.__str__()))
                        continue

            elif action == 'remove':
                if Path(self.mount_path).exists():
                    config.logging.warning('Unexpected Device Removal! : {0} ... Bad =('.format(dev_name))
                else:
                    config.logging.warning('Orderly Removal of : {0} ... Thanks =)'.format(dev_name))



