# app.py

from flask import Flask, jsonify

from utils import get_peru_datetime, peru_timezone
from cronjob import initialize_scheduler
from service import exchange_rate_service, scheduled_task_update_exchange_rate

# Initialize Flask app
app = Flask(__name__)

# Routes
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
    # Initialize scheduler before starting the app
    scheduler = initialize_scheduler(
        function_to_execute=scheduled_task_update_exchange_rate,
        task_id='scheduled_task_update_exchange_rate',
        time_zone=peru_timezone(),
        execution_hour=12,
        execution_minute=40
    )
    
    # Start Flask app
    app.run()
