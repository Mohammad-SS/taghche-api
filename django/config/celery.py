# book_service/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from kombu import Queue, Exchange

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('book_service')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_queues = (
    Queue(name='cache_cleaner', exchange=Exchange(name="books"), routing_key='books.#'),
)

app.conf.task_routes = {
    'books.tasks.clear_book_cache': {
        'exchange': 'books',
        'routing_key': 'books.clear_cache',
        'queue': 'cache_cleaner'
    },
}

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],  # To ensure Celery only accepts JSON
)
app.autodiscover_tasks()
