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

    # Polling Rates
    normal_polling_rate = float(os.environ['normal_polling_rate'])
    logging.debug('Normal Polling Rate: {0}'.format(normal_polling_rate))

    fast_polling_rate = float(os.environ['fast_polling_rate'])
    logging.debug('Fast Polling Rate: {0}'.format(fast_polling_rate))

    fast_polling_rate_enabled_configuration = os.environ['fast_polling_rate_enabled_configuration'].split(',')
    fast_polling = {
        'command': fast_polling_rate_enabled_configuration[0],
        'base_index': int(fast_polling_rate_enabled_configuration[1]),
        'bit_index': int(fast_polling_rate_enabled_configuration[2]),
    }

    # Analog logging variables configuration [MB,59,Gasto,1,-.008]
    #     ---->  1
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

    #     ---->  2
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

    # Digital logging variables configuration [E,24,3,Estado Valvula]
    #     ---->  1
    Dvar1 = os.environ['Dvar1']
    Dvar1 = Dvar1.split(',')
    digital_variable_1 = {
        'command': Dvar1[0],
        'base_index': int(Dvar1[1]),
        'bit_index': int(Dvar1[2]),
        'name': Dvar1[3]
    }

    #     ---->  2
    Dvar2 = os.environ['Dvar2']
    Dvar2 = Dvar2.split(',')
    digital_variable_2 = {
        'command': Dvar2[0],
        'base_index': int(Dvar2[1]),
        'bit_index': int(Dvar2[2]),
        'name': Dvar2[3]
    }

    # Create variables package to poll
    variables = [
        analog_variable_1,
        analog_variable_2,
        digital_variable_1,
        digital_variable_2
    ]


