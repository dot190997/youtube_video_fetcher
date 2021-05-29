import logging
log = logging.getLogger(__name__)

LOG_TYPE_TO_LOGGER = {
    'mismatch': logging.getLogger('mismatchLogger'),
    'request': logging.getLogger('requestLogger'),
    'errorRequest': logging.getLogger('errorRequestLogger'),
    'logger': logging.getLogger('fileLogger')
}


def get_logger(name=None):
    global LOG_TYPE_TO_LOGGER
    return LOG_TYPE_TO_LOGGER.get(name, LOG_TYPE_TO_LOGGER['logger'])
