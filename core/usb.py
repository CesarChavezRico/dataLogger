import config
from pathlib import Path
import pyudev
from subprocess import call, check_output, CalledProcessError
import time
from gpiozero import LED


class USB:
    monitor = None
    mount_path = '/media/usb_storage'
    permanent_mount_path = '/media/permanent_usb_storage'
    permanent_dev_name = '/dev/permanent_usb_drive'

    red_led = None

    def __init__(self):

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
                self.red_led.on()
                devices_count += 1
                config.logging.warning('Trying to mount device #{0}: {1} ...'.format(devices_count, dev_name))
                result = ''

                try:
                    self._mount_usb(self.mount_path, dev_name)
                    try:
                        check_output(['mkdir', '{0}/data_logger'.format(self.mount_path)])
                    except CalledProcessError as e:
                        config.logging.error(
                            f'Error creating [data_logger] directory in external drive, already exists?: {str(e)}')
                        pass

                    result = check_output(['rsync',
                                           '--append',
                                           '-zavh',
                                           '/media/permanent_usb_storage/running',
                                           '/media/permanent_usb_storage/backup'])
                    config.logging.warning('rsync [local backup] output = {0}'.format(result.decode()))
                    result = check_output(['rsync',
                                           '--append',
                                           '--remove-source-files',
                                           '-zavh',
                                           '/media/permanent_usb_storage/running',
                                           '/media/usb_storage/data_logger'])
                    config.logging.warning('rsync [external backup] output = {0}'.format(result.decode()))
                    config.logging.warning('Backup completed! ... Unmounting')

                    try:
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
                    config.logging.error('Fatal error mounting or copying to USB drive: {0}'.format(result))
                    continue

            elif action == 'remove':
                if Path(self.mount_path).exists():
                    config.logging.warning('Unexpected Device Removal! : {0} ... Bad =('.format(dev_name))
                else:
                    config.logging.warning('Orderly Removal of : {0} ... Thanks =)'.format(dev_name))



