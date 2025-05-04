# app.py

from flask import Flask, jsonify, make_response, redirect, url_for
import json

from security import configure_cors
from service import exchange_rate_service

# Application
app = Flask(__name__)

# CORS
app = configure_cors(app,
    origins=[
        'https://brianuceda.vercel.app'
    ]
)

@app.route('/api/v1/<currency_code>', methods=['GET'])
def get_currency_exchange_rate(currency_code):
    return redirect(url_for('convert_currency_amount', currency_code=currency_code, amount=1))

@app.route('/api/v1/<currency_code>/<amount>', methods=['GET'])
def convert_currency_amount(currency_code, amount):
    try:
        result = exchange_rate_service(currency_code, amount)
        
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
