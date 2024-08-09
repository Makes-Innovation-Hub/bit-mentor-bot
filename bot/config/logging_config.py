import logging
import logging.config
from os import path, makedirs

# Create logs directory if it doesn't exist
log_dir = path.join(path.dirname(path.abspath(__file__)), '..', 'logs')
makedirs(log_dir, exist_ok=True)

log_file_path = path.join(log_dir, 'app.log')

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_file_path,
            'formatter': 'standard',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'console': {
            'level': 'ERROR',  # Only print errors to the console
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'DEBUG',
    },
}

# Configure logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)
