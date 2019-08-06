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
                config.logging.info('Mounting Device: {0} ...'.format(dev_mame))
                result = ''
                try:
                    result = check_output(['mkdir', '/media/usbstorage'])
                except CalledProcessError as e:
                    config.logging.info('Fatal error creating mounting directory: {0}'.format(result))
                    if 'File exists' in result:
                        pass
                    else:
                        break
                try:
                    result = check_output(['mount', dev_mame, '/media/usbstorage'])
                    # TODO: Process to copy files
                    check_output(['touch', '/media/usbstorage/{0}'.format(pendulum.now().int_timestamp)])
                    config.logging.info('New File creation completed ... Unmounting')
                    try:
                        check_output(['umount', '/media/usbstorage'])
                    except CalledProcessError as e:
                        output = e.output.decode()
                        config.logging.info('Fatal error creating mounting directory: {0}'.format(output))
                        break
                except CalledProcessError as e:
                    config.logging.info('Fatal error mounting USB drive: {0}'.format(result))
                    break
            elif action == 'remove':
                config.logging.info('Unexpected Device Removal! : {0} ... Bad =('.format(dev_mame))



