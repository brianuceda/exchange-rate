from apscheduler.schedulers.background import BackgroundScheduler

from utils import get_peru_datetime, peru_timezone

def initialize_scheduler(
    function_to_execute,
    id=f"scheduled_task_{get_peru_datetime().strftime('%Y-%m-%d')}",
    hour=1,
    minute=0
):
    scheduler = BackgroundScheduler(timezone=peru_timezone())
    
    print(f"Tarea '{id}' programada a la(s) {hour}:{minute}")
    
    scheduler.add_job(
        func=function_to_execute,
        trigger='cron',
        hour=hour,
        minute=minute,
        id=id,
        max_instances=1,
        coalesce=True
    )
    
    scheduler.start()
    
    function_to_execute()
    
    return scheduler
