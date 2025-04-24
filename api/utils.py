# api/utils.py

import pytz
import datetime

def peru_timezone():
    return pytz.timezone('America/Lima')

def get_peru_datetime():
    return datetime.datetime.now(peru_timezone())
