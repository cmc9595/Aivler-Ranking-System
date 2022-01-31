from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
import sys

def func():
    print('works')

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DJangoJobStore(), "default")
    # cindent causes automatic shift of python comments
    # run this every 1 min
    scheduler.add_job(func, 'interval', minutes=1, name='my', jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("scheduler started...", file=sys.stdout)

