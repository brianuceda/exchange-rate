from flask import Flask, jsonify
import redis
import os
# import requests
# from bs4 import BeautifulSoup
# import datetime

app = Flask(__name__)

# Configuración de Redis
redis_client = redis.Redis(
    host=os.environ.get('EXCHANGERATE_REDIS_HOST'),
    port=int(os.environ.get('EXCHANGERATE_REDIS_PORT')),
    password=os.environ.get('EXCHANGERATE_REDIS_PASSWORD'),
    db=int(os.environ.get('EXCHANGERATE_REDIS_DB')),
    decode_responses=True
)

@app.route('/test')
def home():
    try:
        redis_client.ping()
        return jsonify(message="Redis connected successfully"), 200
    except Exception as e:
        return jsonify(message=str(e)), 500

if __name__ == '__main__':
    app.run()
