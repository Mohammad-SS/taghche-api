from config.celery import app
from django.conf import settings
from requests import request
from django.urls import reverse
from .classes import Book
import json

@app.task
def clear_book_cache(book_id, delete_from=None):
    if delete_from is None:
        delete_from = settings.CACHES

    result = {}
    endpoint = reverse("get-book", kwargs={"book_id": book_id})
    url = f"http://django:8000{endpoint}"
    headers = {
        "Authorization": f"Bearer {settings.CELERY_SECRET_KEY}"
    }
    for cache in delete_from:
        response = request(method="DELETE", url=url, data={"cache": cache}, headers=headers)
        if response.status_code != 200:
            result[cache] = response.json()
        else:
            result[cache] = response.text
    return result


@app.task
def refresh_book_cache(book_id, update_in=None):
    if update_in is None:
        update_in = settings.CACHES

    result = {}
    endpoint = reverse("get-book", kwargs={"book_id": book_id})
    url = f"http://django:8000{endpoint}"
    headers = {
        "Authorization": f"Bearer {settings.CELERY_SECRET_KEY}"
    }
    book = Book(book_id=book_id)
    data = json.dumps(book.fetch_book_data())
    if data:
        for cache in update_in:
            response = request(method="PUT", url=url, data={"cache": cache, "data": data}, headers=headers)
            if response.status_code != 200:
                result[cache] = response.json()
            else:
                result[cache] = response.text
        return result
    else:
        return {"error" : "it seems Taagche API is down !"}
