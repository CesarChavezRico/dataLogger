import logging
import os
import sys

console_only = os.environ['console_only']
logging.warning("Environment Variable: console_only = {0}".format(console_only))

if console_only == 'True':
    pass

else:
    # Logging configuration
    logging_level = int(os.environ['logging'])
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - [%(levelname)s]: %(message)s',
                        level=logging_level)
    logging.getLogger().setLevel(logging_level)
    logging.warning("Environment Variable: logging_level = {0}".format(logging_level))

    # Polling Rate
    rate = int(os.environ['polling_rate'])
    logging.debug('Polling Rate: {0}'.format(rate))

    # Analog logging variables configuration
    # 1
    Avar1 = os.environ['Avar1']
    Avar1 = Avar1.split(',')
    analog_variable_1 = {
        'command': Avar1[0],
        'base_index': int(Avar1[1]),
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
        'base_index': int(Avar2[1]),
        'name': Avar2[2],
        'm': float(Avar2[3]),
        'b': float(Avar2[4])
    }
    logging.debug('Analog Variable 2 - Configuration:\n{0}'.format(analog_variable_2))

    # Create variables package to poll
    variables = [
        analog_variable_1,
        analog_variable_2
    ]


