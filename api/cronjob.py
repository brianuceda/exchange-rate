from apscheduler.schedulers.background import BackgroundScheduler

def initialize_scheduler(
    function_to_execute,
    task_id='scheduled_task',
    time_zone='America/Lima',
    execution_hour=1,
    execution_minute=0
):
    scheduler = BackgroundScheduler(timezone=time_zone)
    
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
