import logging
import os
import sys

console_only = os.environ['console_only']
logging.warning("Environment Variable: console_only = {0}".format(console_only))

if console_only == 'True':
    pass

else:
    # Analog logging variables configuration
    # 1
    Avar1 = os.environ['Avar1']
    Avar1 = Avar1.split(',')
    analog_variable_1 = {
        'command': Avar1[0],
        'base_index': Avar1[1],
        'name': Avar1[2],
        'm': float(Avar1[3]),
        'b': float(Avar1[4])
    }
    logging.debug('Analog Variable 1 - Configuration:\n{0}'.format(analog_variable_1))

    # 2
    Avar2 = os.environ['Avar2']
    Avar2 = Avar2.split(',')
    analog_variable_2 = {
        'command': Avar2[0],
        'base_index': Avar2[1],
        'name': Avar2[2],
        'm': float(Avar2[3]),
        'b': float(Avar2[4])
    }
    logging.debug('Analog Variable 2 - Configuration:\n{0}'.format(analog_variable_2))

    # Logging configuration
    logging_level = int(os.environ['logging'])
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - [%(levelname)s]: %(message)s',
                        level=logging_level)
    logging.getLogger().setLevel(logging_level)
    logging.warning("Environment Variable: logging_level = {0}".format(logging_level))
