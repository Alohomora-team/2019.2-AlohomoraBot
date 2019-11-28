"""
Util functions
"""

import logging

from settings import LOG_NAME

logger = logging.getLogger(LOG_NAME)

def format_datetime(value):
    """
    Parse date string
    """
    logger.info(value)

    date = value[0:10]
    time = value[11:16]

    day = date[8:10]
    month = date[5:7]
    year = date[0:4]

    datetime = day + '/' + month + '/' + year + ' ' + time

    logger.info(datetime)

    return datetime
