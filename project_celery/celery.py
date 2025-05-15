#celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_celery.settings')

app = Celery('project_celery', backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')
app.conf.broker_url = 'redis://localhost:6379/0'
app.config_from_object('django.conf:settings', namespace='')
app.autodiscover_tasks()
