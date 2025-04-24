# app.py

from flask import Flask, jsonify

from utils import get_peru_datetime
from cronjob import initialize_scheduler
from service import exchange_rate_service, scheduled_task_update_exchange_rate

app = Flask(__name__)

scheduler = initialize_scheduler(
    function_to_execute=scheduled_task_update_exchange_rate,
    task_id='scheduled_task_update_exchange_rate',
    execution_hour=13,
    execution_minute=1
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
