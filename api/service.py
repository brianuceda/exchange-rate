from datetime import datetime, timedelta, timezone
import os
import time
import redis
import requests
from dotenv import load_dotenv

from utils import get_peru_datetime, get_currency_symbols

load_dotenv()

CURRENCY_SYMBOLS = get_currency_symbols()

redis_client = redis.Redis(
    host=os.environ.get('EXCHANGERATE_REDIS_HOST'),
    port=int(os.environ.get('EXCHANGERATE_REDIS_PORT')),
    password=os.environ.get('EXCHANGERATE_REDIS_PASSWORD'),
    db=int(os.environ.get('EXCHANGERATE_REDIS_DB')),
    decode_responses=True
)

def get_exchange_rate_from_web(currency_code="PEN"):
    try:
        # Validate currency code
        currency_code = currency_code.upper()
        if currency_code not in CURRENCY_SYMBOLS:
            return {"error": f"Currency code '{currency_code}' not supported"}
        
        # Fetch exchange rate data
        url = f"https://open.er-api.com/v6/latest/{currency_code}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if 'rates' in data:
            conversions = {}
            
            for code in CURRENCY_SYMBOLS:
                if code != currency_code and code in data['rates']:
                    # Preserve 6 decimal places maximum
                    converted_value = round(data['rates'][code], 6)
                    conversions[code] = {
                        "value": converted_value,
                        "symbol": CURRENCY_SYMBOLS[code],
                        "formatted": f"{CURRENCY_SYMBOLS[code]} {converted_value}"
                    }
            
            return {
                "base": currency_code,
                "amount": 1,
                "time_last_update_peru": datetime.fromtimestamp(data['time_last_update_unix'], timezone(timedelta(hours=-5))).strftime('%Y-%m-%dT%H:%M'),
                "time_next_update_peru": datetime.fromtimestamp(data['time_next_update_unix'], timezone(timedelta(hours=-5))).strftime('%Y-%m-%dT%H:%M'),
                "conversions": conversions
            }
        else:
            return {"error": "No se encontraron tasas en la respuesta"}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Error de solicitud: {str(e)}"}
    except Exception as e:
        return {"error": f"Error general: {str(e)}"}

def apply_amount_to_conversions(exchange_data, amount):
    if not exchange_data or "error" in exchange_data:
        return exchange_data
    
    result = exchange_data.copy()
    result["amount"] = amount
    
    # Apply the amount to each conversion
    for code, conversion in result["conversions"].items():
        original_value = conversion["value"]
        # Calculate with 6 decimal places maximum
        new_value = round(original_value * amount, 6)
        result["conversions"][code]["value"] = new_value
        result["conversions"][code]["formatted"] = f"{conversion['symbol']} {new_value}"
    
    return result

def exchange_rate_service(currency_code="PEN", amount=1):
    currency_code = currency_code.upper()
    
    date = get_peru_datetime().strftime('%Y-%m-%d')
    redis_key = f'exchange_rate:{currency_code}:{date}'
    
    # Validations
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return {"error": f"Cantidad inválida: {amount}. Debe ser un número."}
    
    if currency_code not in CURRENCY_SYMBOLS:
        return {"error": f"Código de moneda '{currency_code}' no soportado"}
    
    # Try to get from Redis
    cached_data = redis_client.get(redis_key)
    if cached_data:
        base_data = eval(cached_data)
        return apply_amount_to_conversions(base_data, amount)
    
    # If not in cache, get from web
    exchange_data = get_exchange_rate_from_web(currency_code)
    if exchange_data and "error" not in exchange_data:
        expiration_time = 24 * 60 * 60 + 5 * 60  # 1 day and 5 minutes
        redis_client.setex(redis_key, expiration_time, str(exchange_data))
        return apply_amount_to_conversions(exchange_data, amount)
    
    return exchange_data

# Cronjob function (simulation of controller)
def scheduled_task_update_exchange_rate():
    try:
        print(f"Ejecutando tarea programada: {get_peru_datetime()}")
        
        result = exchange_rate_service("PEN", 1)
        time.sleep(1)
        result = exchange_rate_service("USD", 1)
        time.sleep(1)
        result = exchange_rate_service("CAD", 1)
        time.sleep(1)
        result = exchange_rate_service("EUR", 1)
        
        if result:
            print(f"Actualización exitosa.")
        else:
            print("Actualización fallida.")
    except Exception as e:
        print(f"Error en la actualización programada: {str(e)}")
