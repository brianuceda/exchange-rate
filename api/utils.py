# api/utils.py

import logging
import pytz
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_logger():
    return logger

# Configure timezone
def peru_timezone():
    return pytz.timezone('America/Lima')

# Service functions
def get_peru_datetime():
    return datetime.datetime.now(peru_timezone())
