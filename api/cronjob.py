from apscheduler.schedulers.background import BackgroundScheduler

from utils import peru_timezone

def initialize_scheduler(
    function_to_execute,
    task_id='scheduled_task',
    execution_hour=1,
    execution_minute=0
):
    scheduler = BackgroundScheduler(timezone=peru_timezone())
    
    print(f"Tarea '{task_id}' programada a la(s) {execution_hour}:{execution_minute}")
    
    scheduler.add_job(
        func=function_to_execute,
        trigger='cron',
        hour=execution_hour,
        minute=execution_minute,
        id=task_id,
        max_instances=1,
        coalesce=True
    )
    
    scheduler.start()
    
    function_to_execute()
    
    return scheduler
