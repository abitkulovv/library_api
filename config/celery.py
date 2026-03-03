import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("library_api")
app.config_from_object("django.conf:settings", namespace="CELERY")


app.conf.beat_schedule = {
    "new_books_every_day": {
        "task": "apps.books.tasks.send_new_books_notifications",
        "schedule": crontab(hour=9, minute=0),
    },
    "anniversary_books_every_day": {
        "task": "apps.books.tasks.send_anniversary_books_notifications",
        "schedule": crontab(hour=10, minute=0),
    },
}

app.autodiscover_tasks()