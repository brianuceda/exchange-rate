# app.py

from flask import Flask, jsonify

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

@app.route('/api/v1/today', methods=['GET'])
def get_today_exchange_rate():
    try:
        today = get_peru_datetime().strftime('%Y-%m-%d')
        result = exchange_rate_service(today)
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"error": "No se pudo obtener la tasa de cambio"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':    
    app.run()
