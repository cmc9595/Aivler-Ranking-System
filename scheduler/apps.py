from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduler'

class AppNameConfig(AppConfig):
    name = 'scheduler'
    def ready(self):
        from scheduler import scheduler
        scheduler.start()
