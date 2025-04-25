# app.py

from bs4 import BeautifulSoup
from flask import Flask, jsonify, make_response, redirect, url_for
import requests
import json

from security import configure_cors

from service import exchange_rate_service, scheduled_task_update_exchange_rate
from cronjob import initialize_scheduler

from utils import get_peru_datetime

# Application
app = Flask(__name__)

# CORS
app = configure_cors(app,
    origins=[
        'https://brianuceda.vercel.app'
    ]
)

# Cronjob
scheduler = initialize_scheduler(
    function_to_execute=scheduled_task_update_exchange_rate,
    id='scheduled_task_update_exchange_rate',
    hour=0,
    minute=1
)

# Constantes
CURRENCY_SYMBOLS = {
    "PEN": "S/",
    "USD": "$",
    "CAD": "$",
    "EUR": "€",
}

@app.route('/api/v1/<currency_code>', methods=['GET'])
def get_currency_exchange_rate(currency_code):
    return redirect(url_for('convert_currency_amount', currency_code=currency_code, amount=1))

@app.route('/api/v1/<currency_code>/<amount>', methods=['GET'])
def convert_currency_amount(currency_code, amount):
    try:
        date = get_peru_datetime().strftime('%Y-%m-%d')
        
        currency_code = currency_code.upper()
        amount = float(amount)
        result = exchange_rate_service(date, currency_code, amount)
        
        if result and "error" not in result:
            response_json = json.dumps(result, indent=2)
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response, 200
        else:
            error_message = result.get("error", "Could not get exchange rate") if result else "No data returned"
            return jsonify({"error": error_message}), 400
            
    except Exception as e:
        print(f"Error general: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':    
    app.run(debug=True)
