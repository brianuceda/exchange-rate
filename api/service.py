import os
import time
import redis
from dotenv import load_dotenv

from utils import get_logger, get_peru_datetime

load_dotenv()

redis_client = redis.Redis(
    host=os.environ.get('EXCHANGERATE_REDIS_HOST'),
    port=int(os.environ.get('EXCHANGERATE_REDIS_PORT')),
    password=os.environ.get('EXCHANGERATE_REDIS_PASSWORD'),
    db=int(os.environ.get('EXCHANGERATE_REDIS_DB')),
    decode_responses=True
)

def get_exchange_rate_from_web(date_str=None):
    now = get_peru_datetime()
    time.sleep(5)
    return {
        "message": "Ok",
        "date": date_str or now.strftime('%Y-%m-%d'),
    }

def exchange_rate_service(date_key=None):
    redis_key = f'exchange_rate:{date_key}'
    
    # Try to get from Redis
    cached_data = redis_client.get(redis_key)
    if cached_data:
        data = eval(cached_data)
        return data
    
    # If not in cache, get from web
    exchange_data = get_exchange_rate_from_web(date_key)
    if exchange_data:
        expiration_time = 24 * 60 * 60 + 5 * 60  # 1 day and 5 minutes
        redis_client.setex(redis_key, expiration_time, str(exchange_data))
        return exchange_data
    
    return None

# Cronjob function (simulation of controller)
def scheduled_task_update_exchange_rate():
    try:
        get_logger().info(f"Ejecutando tarea programada: {get_peru_datetime()}")
        
        today = get_peru_datetime().strftime('%Y-%m-%d')
        result = exchange_rate_service(today)
        
        if result:
            get_logger().info(f"Actualización exitosa.")
        else:
            get_logger().error("Actualización fallida.")
    except Exception as e:
        get_logger().error(f"Error en la actualización programada: {str(e)}")