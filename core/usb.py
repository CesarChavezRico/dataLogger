import config
from pathlib import Path
import pyudev
from subprocess import call, check_output, CalledProcessError
import time


class USB:
    monitor = None
    mount_path = '/media/usb_storage'
    permanent_mount_path = '/media/permanent_usb_ storage'
    permanent_dev_name = 'dev/permanent_usb_drive'

    def __init__(self):
        context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(context, source=u'kernel')
        call(["udevadm", "trigger"])  # Make sure that UDEV rules executed
        self._mount_usb(self.permanent_mount_path, self.permanent_dev_name)  # Mount our permanent USB drive

    def _mount_usb(self, mount_path, dev_name):
        try:
            result = check_output(['mkdir', mount_path])
        except CalledProcessError as e:
            # Adding 4 seconds last 3 led´s yellow for error on mounting directory
            # TODO: add led signaling
            # time.sleep(4)
            config.logging.error('Error creating mounting directory for device #{0}: {1}'.format(devices_count,
                                                                                                 str(e)))
            # Maybe the directory is already created, all good
            pass
        finally:
            check_output(['mount', dev_name, self.mount_path])

    def check_for_devices(self):
        devices_count = 0
        # Filter for 'Block' devices
        self.monitor.filter_by('block')
        for action, device in self.monitor:
            dev_name = device.get('DEVNAME')
            config.logging.info('{0}: {1}'.format(action, dev_name))
            if action == 'add':
                devices_count += 1
                config.logging.warning('Trying to mount device #{0}: {1} ...'.format(devices_count, dev_name))
                result = ''
                try:
                    self._mount_usb(self.mount_path, dev_name)
                    result = check_output(['rsync',
                                           '--append',
                                           '--remove-source-files',
                                           '-zavh',
                                           '/media/permanent_usb_storage',
                                           '/media/usb_storage/'])
                    config.logging.warning('rsync output = {0}'.format(result.decode()))
                    # Adding 4 seconds on back up completed
                    # TODO: add led signaling
                    # time.sleep(4)
                    config.logging.warning('Backup completed! ... Unmounting')
                    # TODO: add led signaling
                    try:
                        check_output(['umount', self.mount_path])
                    except CalledProcessError as e:
                        output = e.output.decode()
                        # Adding 4 seconds last 3 led´s red for Fatal error
                        # TODO: add led signaling
                        time.sleep(4)
                        config.logging.error('Fatal error unmounting device #{0}: {1}'.format(devices_count,output))
                        # TODO: add led signaling
                        # Lets try with next device if available
                        continue
                    try:
                        check_output(['rm', '-r', self.mount_path])
                    except CalledProcessError as e:
                        # Adding 4 seconds last 3 led´s red for Fatal error
                        # TODO: add led signaling
                        # time.sleep(4)
                        output = e.output.decode()
                        config.logging.error('Fatal error removing mounting directory for device #{0}: {1}'
                                             .format(devices_count, output))
                        # TODO: add led signaling
                        # Lets try with next device if available
                        continue
                except CalledProcessError as e:
                    # Adding 4 seconds all led red for Fatal error
                    # TODO: add led signaling
                    # time.sleep(4)
                    config.logging.error('Fatal error mounting or copying to USB drive: {0}'.format(result))
                    # TODO: add led signaling
                    # Lets try with next device if available
                    continue
            elif action == 'remove':
                if Path(self.mount_path).exists():
                    config.logging.warning('Unexpected Device Removal! : {0} ... Bad =('.format(dev_name))
                else:
                    config.logging.warning('Orderly Removal of : {0} ... Thanks =)'.format(dev_name))



