import config
import pendulum
import pyudev
from subprocess import check_output, CalledProcessError


class USB:
    monitor = None

    def __init__(self):
        context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(context, source=u'kernel')

    def check_for_devices(self):
        # Filter for 'Block' devices
        self.monitor.filter_by('block')
        for action, device in self.monitor:
            dev_mame = device.get('DEVNAME')
            config.logging.info('{0}: {1}'.format(action, dev_mame))
            if action == 'add':
                config.logging.warning('Mounting Device: {0} ...'.format(dev_mame))
                result = ''
                try:
                    result = check_output(['mkdir', '/media/usbstorage'])
                except CalledProcessError as e:
                    config.logging.error('Error creating mounting directory: {0}'.format(str(e)))
                    pass
                try:
                    result = check_output(['mount', dev_mame, '/media/usbstorage'])
                    result = check_output(['rsync',
                                           '--append',
                                           '--remove-source-files',
                                           '-zavh',
                                           '/data/',
                                           '/media/usbstorage/'])
                    config.logging.warning('rsync output = {0}'.format(result.decode()))
                    config.logging.warning('Backup completed! ... Unmounting')
                    try:
                        check_output(['umount', '/media/usbstorage'])
                    except CalledProcessError as e:
                        output = e.output.decode()
                        config.logging.error('Fatal error unmounting device: {0}'.format(output))
                        break
                    try:
                        check_output(['rm', '-r' '/media/usbstorage'])
                    except CalledProcessError as e:
                        output = e.output.decode()
                        config.logging.error('Fatal error removing mounting directory: {0}'.format(output))
                        break
                except CalledProcessError as e:
                    config.logging.error('Fatal error mounting or copying to USB drive: {0}'.format(result))
                    break
            elif action == 'remove':
                config.logging.warning('Unexpected Device Removal! : {0} ... Bad =('.format(dev_mame))



