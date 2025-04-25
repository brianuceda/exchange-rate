import os
import time
import redis
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

def get_exchange_rate_from_web(date=None):
    time.sleep(5)
    return {
        "message": "Ok",
        "date": date,
    }

def exchange_rate_service(date=None):
    redis_key = f'exchange_rate:{date}'
    
    # Try to get from Redis
    cached_data = redis_client.get(redis_key)
    if cached_data:
        data = eval(cached_data)
        return data
    
    # If not in cache, get from web
    exchange_data = get_exchange_rate_from_web(date)
    if exchange_data:
        expiration_time = 24 * 60 * 60 + 5 * 60  # 1 day and 5 minutes
        redis_client.setex(redis_key, expiration_time, str(exchange_data))
        return exchange_data
    
    return None

# Cronjob function (simulation of controller)
def scheduled_task_update_exchange_rate():
    try:
        print(f"Ejecutando tarea programada: {get_peru_datetime()}")
        
        today = get_peru_datetime().strftime('%Y-%m-%d')
        result = exchange_rate_service(today)
        
        if result:
            print(f"Actualización exitosa.")
        else:
            print("Actualización fallida.")
    except Exception as e:
        print(f"Error en la actualización programada: {str(e)}")
