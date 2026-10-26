# core/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')

# automatically discover tasks in installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
