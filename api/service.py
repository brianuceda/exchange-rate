import os
import time
import redis
import requests
from dotenv import load_dotenv

from utils import get_peru_datetime

load_dotenv()

redis_client = redis.Redis(
    host=os.environ.get('EXCHANGERATE_REDIS_HOST'),
    port=int(os.environ.get('EXCHANGERATE_REDIS_PORT')),
    password=os.environ.get('EXCHANGERATE_REDIS_PASSWORD'),
    db=int(os.environ.get('EXCHANGERATE_REDIS_DB')),
    decode_responses=True
)

# Constantes
CURRENCY_SYMBOLS = {
    "PEN": "S/",
    "USD": "$",
    "CAD": "$",
    "EUR": "€",
}

def get_exchange_rate_from_web(date=None, currency_code="USD", amount=1):
    """
    Fetch exchange rate data from the web
    
    Args:
        date: Date to use for caching (Peru time)
        currency_code: Base currency code (USD, PEN, etc.)
        amount: Amount to convert (default: 1)
    
    Returns:
        dict: Exchange rate data
    """
    try:
        # Validate currency code
        currency_code = currency_code.upper()
        if currency_code not in CURRENCY_SYMBOLS:
            return {"error": f"Currency code '{currency_code}' not supported"}
        
        # Validate amount
        try:
            amount_value = float(amount)
        except ValueError:
            return {"error": f"Invalid amount: {amount}. Must be a number."}
        
        # Fetch exchange rate data
        url = f"https://api.exchangerate-api.com/v4/latest/{currency_code}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if 'rates' in data:
            conversions = {}
            
            for code in CURRENCY_SYMBOLS:
                if code != currency_code and code in data['rates']:
                    converted_value = round(amount_value * data['rates'][code], 2)
                    conversions[code] = {
                        "value": converted_value,
                        "symbol": CURRENCY_SYMBOLS[code],
                        "formatted": f"{CURRENCY_SYMBOLS[code]} {converted_value}"
                    }
            
            return {
                "base": currency_code,
                "amount": amount_value,
                "date": data['date'],
                "time_last_updated": data['time_last_updated'],
                "conversions": conversions
            }
        else:
            return {"error": "Could not find rates in response"}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"General error: {str(e)}"}

def exchange_rate_service(date=None, currency_code="PEN", amount=1):
    redis_key = f'exchange_rate:{currency_code}:{amount}:{date}'
    
    # Try to get from Redis
    cached_data = redis_client.get(redis_key)
    if cached_data:
        data = eval(cached_data)
        return data
    
    # If not in cache, get from web
    exchange_data = get_exchange_rate_from_web(date, currency_code, amount)
    if exchange_data and "error" not in exchange_data:
        expiration_time = 24 * 60 * 60 + 5 * 60  # 1 day and 5 minutes
        redis_client.setex(redis_key, expiration_time, str(exchange_data))
        return exchange_data
    
    return exchange_data

# Cronjob function (simulation of controller)
def scheduled_task_update_exchange_rate():
    try:
        print(f"Ejecutando tarea programada: {get_peru_datetime()}")
        
        today = get_peru_datetime().strftime('%Y-%m-%d')
        result = exchange_rate_service(today, "PEN", 1)
        time.sleep(1)
        result = exchange_rate_service(today, "USD", 1)
        time.sleep(1)
        result = exchange_rate_service(today, "CAD", 1)
        time.sleep(1)
        result = exchange_rate_service(today, "EUR", 1)
        
        if result:
            print(f"Actualización exitosa.")
        else:
            print("Actualización fallida.")
    except Exception as e:
        print(f"Error en la actualización programada: {str(e)}")
