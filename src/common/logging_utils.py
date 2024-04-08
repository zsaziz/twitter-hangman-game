# local lib
from src.common.date_utils import get_todays_date_time

# python lib
import logging
import os

LOGS_PATH = os.path.abspath(f'logs/hangman-{get_todays_date_time()}.log')


def get_logger(namespace=__name__, save_file=False):
    logging.basicConfig(filename=LOGS_PATH if save_file else None,
                        format='%(asctime)s:%(name)s:%(levelname)s: %(message)s', datefmt='%m/%d/%Y-%I:%M:%S:%p',
                        level=logging.INFO)
    logger = logging.getLogger(namespace)
    logger.setLevel(logging.INFO)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger
