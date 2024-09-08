import logging
from logging.handlers import RotatingFileHandler
import os
import uuid


def generate_request_id():
    return str(uuid.uuid4())


class ExtendedLogFilter(logging.Filter):
    def __init__(self, request_id=None, user=None, handler=None):
        super().__init__()
        self.request_id = request_id
        self.user = user
        self.handler = handler

    def update(self, request_id=None, user=None, handler=None):
        if request_id:
            self.request_id = request_id
        if user:
            self.user = user
        if handler:
            self.handler = handler

    def filter(self, record):
        record.request_id = self.request_id if self.request_id else 'no-request-id'
        record.user = self.user if self.user else 'anonymous'
        record.handler = self.handler if self.handler else 'no-handler'
        return True


def setup_logger(request_id=None, user=None, handler_name=None):
    logger_name = 'app_logger'
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        log_directory = os.path.join(base_directory, 'logs')
        if not os.path.exists(log_directory):
            print(f"Creating log directory: {log_directory}")
            os.makedirs(log_directory)
        
        log_file = os.path.join(log_directory, 'app.log')
        if os.path.exists(log_file):
            os.remove(log_file)
            
        handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(request_id)s - %(user)s - %(handler)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Apply the extended filter
        filter = ExtendedLogFilter(request_id=request_id, user=user, handler=handler_name)
        handler.addFilter(filter)
        logger.addHandler(handler)
    else:
        for handler in logger.handlers:
            for filter in handler.filters:
                if isinstance(filter, ExtendedLogFilter):
                    filter.update(request_id=request_id, user=user, handler=handler_name)

    return logger


# Initialize the logger with default values for now
app_logger = setup_logger()
