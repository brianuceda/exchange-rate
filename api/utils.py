# api/utils.py

import pytz
import datetime

def get_currency_symbols():
    return {
        "PEN": "S/",
        "USD": "$",
        "CAD": "$",
        "EUR": "€",
    }

def peru_timezone():
    return pytz.timezone('America/Lima')

def get_peru_datetime():
    return datetime.datetime.now(peru_timezone())
