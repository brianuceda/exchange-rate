from apscheduler.schedulers.background import BackgroundScheduler

from utils import get_logger, peru_timezone

def initialize_scheduler(
    function_to_execute,
    task_id='scheduled_task',
    time_zone='America/Lima',
    execution_hour=1,
    execution_minute=0
):
    scheduler = BackgroundScheduler(timezone=time_zone)
    
    get_logger().info(f"Tarea '{task_id}' programada a la(s) {execution_hour}:{execution_minute}")
    
    # Schedule task to run
    scheduler.add_job(
        func=function_to_execute,
        trigger='cron',
        hour=execution_hour,
        minute=execution_minute,
        id=task_id,
        max_instances=1,
        coalesce=True
    )
    
    # Start scheduler
    scheduler.start()
    
    # Run the task once at startup to verify it works
    function_to_execute()
    
    return scheduler
