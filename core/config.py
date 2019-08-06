import os
import logging

console_only = os.environ['console_only']
logging.warning("Environment Variable: console_only = {0}".format(console_only))

if console_only == 'True':
    pass

else:
    logging_level = int(os.environ['logging'])
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - [%(levelname)s]: %(message)s',
                        level=logging_level)
    logging.getLogger().setLevel(logging_level)
    logging.warning("Environment Variable: logging_level = {0}".format(logging_level))
