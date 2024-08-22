from config.celery import app
from django.conf import settings
from requests import request
from django.urls import reverse


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
