# app.py

from bs4 import BeautifulSoup
from flask import Flask, jsonify, make_response
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
    hour=1,
    minute=0
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
    # Validate currency code
    currency_code = currency_code.upper()
    if currency_code not in CURRENCY_SYMBOLS:
        return jsonify({"error": f"Currency code '{currency_code}' not supported"}), 400
    
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{currency_code}"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if 'rates' in data:
            rates = {}
            
            for code in CURRENCY_SYMBOLS:
                if code != currency_code and code in data['rates']:
                    rates[code] = {
                        "value": data['rates'][code],
                        "symbol": CURRENCY_SYMBOLS[code]
                    }
            
            response_json = json.dumps({
                "base": currency_code,
                "date": data['date'],
                "time_last_updated": data['time_last_updated'],
                "rates": rates
            }, indent=2)
            
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            
            return response, 200
        else:
            return jsonify({"error": "Could not find rates in response"}), 500
            
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Error general: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/<currency_code>/<amount>', methods=['GET'])
def convert_currency_amount(currency_code, amount):
    # Validate currency code
    currency_code = currency_code.upper()
    if currency_code not in CURRENCY_SYMBOLS:
        return jsonify({"error": f"Currency code '{currency_code}' not supported"}), 400
    
    # Validate amount
    try:
        amount_value = float(amount)
    except ValueError:
        return jsonify({"error": f"Invalid amount: {amount}. Must be a number."}), 400
    
    try:
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
            
            response_json = json.dumps({
                "base": currency_code,
                "amount": amount_value,
                "date": data['date'],
                "time_last_updated": data['time_last_updated'],
                "conversions": conversions
            }, indent=2)
            
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            
            return response, 200
        else:
            return jsonify({"error": "Could not find rates in response"}), 500
            
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Error general: {e}")
        return jsonify({"error": str(e)}), 500

    # Real Controller
    # try:
    #     date = get_peru_datetime().strftime('%Y-%m-%d')
    #     result = exchange_rate_service(date)
    #     if result:
    #         return jsonify(result), 200
    #     else:
    #         return jsonify({"error": "No se pudo obtener la tasa de cambio"}), 500
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

if __name__ == '__main__':    
    app.run(debug=True)
