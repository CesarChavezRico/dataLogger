import config
from pathlib import Path
import os
import pyudev
from subprocess import call, check_output, CalledProcessError
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
            check_output(['mkdir', '{0}/running'.format(self.permanent_mount_path)])
        except CalledProcessError as e:
            config.logging.error(
                'Error creating [running] directory already exists?: {0}'.format(str(e)))
            pass

        try:
            check_output(['mkdir', '{0}/backup'.format(self.permanent_mount_path)])
        except CalledProcessError as e:
            config.logging.error(
                'Error creating [backup] directory, already exists?: {0}'.format(str(e)))
            pass

        # Init LEDs
        self.red_led = LED(23)

    @staticmethod
    def _mount_usb(mount_path, dev_name):
        try:
            check_output(['mkdir', mount_path])
        except CalledProcessError as e:
            config.logging.error('Error creating mounting directory for device #{0}: {1}'.format(dev_name, str(e)))
            pass
        finally:
            check_output(['mount', dev_name, mount_path])

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
                            check_output(['mkdir', '{0}/data_logger'.format(self.mount_path)])
                        except CalledProcessError as e:
                            config.logging.error(
                                f'Error creating [data_logger] directory in external drive, already exists?: {str(e)}')
                            pass
                        files = os.listdir(f'{self.permanent_mount_path}/running/')
                        try:
                            for file in files:
                                destination_file = Path(f'{self.mount_path}/data_logger/{file}')
                                if destination_file.is_file():
                                    config.logging.warning(f'[external backup] [{file}] already exists in destination'
                                                           f' - Appending')
                                    with open(file, 'r') as source_file:
                                        contents = source_file.read()
                                        with open(destination_file, 'a') as des_file:
                                            des_file.write(contents)

                                else:
                                    config.logging.warning(f'[external backup] [{file}] not found in destination'
                                                           f' - Just copying')
                                    result = check_output(['cp',
                                                           f'{self.permanent_mount_path}/{file}',
                                                           f'{self.mount_path}/data_logger/{file}'])
                                    config.logging.warning(f'[external backup] [cp] output = {result.decode}')

                                config.logging.warning(f'[external backup] deleting internal [{file}]')
                                result = check_output(['rm', f'{self.permanent_mount_path}/{file}'])
                                config.logging.warning(f'[external backup] [rm] output = {result.decode}')

                        except CalledProcessError as e:
                            config.logging.error(
                                f'Fatal Error backing up [{file}]: {str(e)}')
                            continue
                        try:
                            config.logging.warning('Backup completed! ... Unmounting')
                            check_output(['umount', self.mount_path])
                        except CalledProcessError as e:
                            output = e.output.decode()
                            config.logging.error('Fatal error unmounting device #{0}: {1}'.format(devices_count,output))
                            continue
                        try:
                            check_output(['rm', '-r', self.mount_path])
                        except CalledProcessError as e:
                            output = e.output.decode()
                            config.logging.error('Fatal error removing mounting directory for device #{0}: {1}'
                                                 .format(devices_count, output))
                            continue
                        self.red_led.off()

                    except CalledProcessError as e:
                        config.logging.error('Fatal error mounting or copying to USB drive: {0}'.format(e.__str__()))
                        continue

            elif action == 'remove':
                if Path(self.mount_path).exists():
                    config.logging.warning('Unexpected Device Removal! : {0} ... Bad =('.format(dev_name))
                else:
                    config.logging.warning('Orderly Removal of : {0} ... Thanks =)'.format(dev_name))



