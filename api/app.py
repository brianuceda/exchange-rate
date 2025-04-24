from flask import Flask, jsonify
import redis
import os
import requests
from bs4 import BeautifulSoup
import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

# Configuración de zona horaria para Perú
peru_timezone = pytz.timezone('America/Lima')

app = Flask(__name__)

# Configuración de Redis
redis_client = redis.Redis(
    host=os.environ.get('EXCHANGERATE_REDIS_HOST'),
    port=int(os.environ.get('EXCHANGERATE_REDIS_PORT')),
    password=os.environ.get('EXCHANGERATE_REDIS_PASSWORD'),
    db=int(os.environ.get('EXCHANGERATE_REDIS_DB')),
    decode_responses=True
)

@app.route('/today')
def exchange_rate_controller():
    try:
        redis_client.ping()
        return jsonify(message="Redis connected successfully - " + str(get_peru_datetime())), 200
    except Exception as e:
        return jsonify(message=str(e)), 500

def exchange_rate_service():
    return jsonify(message="Exchange rate service")

# Función de utilidad para obtener la fecha y hora actual en zona horaria de Perú
def get_peru_datetime():
    return datetime.datetime.now(peru_timezone)

if __name__ == '__main__':
    app.run(debug=True)
