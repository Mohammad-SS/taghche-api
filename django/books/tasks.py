from config.celery import app
from django.conf import settings
from requests import request
from django.urls import reverse
from .classes import Book
import json


@app.task
def clear_book_cache(book_id, delete_from=None):
    """
    Celery task to clear the cached data for a specific book across multiple caches.

    This function sends DELETE requests to the specified caches to remove the book data.

    Args:
        book_id (str): The unique identifier for the book.
        delete_from (list, optional): A list of cache names from which to delete the data.
                                      Defaults to all caches defined in settings.CACHES.

    Returns:
        dict: A dictionary with cache names as keys and the server's response as values.
    """
    if delete_from is None:
        delete_from = settings.CACHES

    result = {}
    endpoint = reverse("get-book", kwargs={"book_id": book_id})
    url = f"http://django:8000{endpoint}"
    headers = {"Authorization": f"Bearer {settings.CELERY_SECRET_KEY}"}

    # Iterate through the specified caches and send a DELETE request to clear the cache.
    for cache in delete_from:
        response = request(
            method="DELETE", url=url, data={"cache": cache}, headers=headers
        )
        if response.status_code != 200:
            result[cache] = (
                response.json()
            )  # Record the JSON response if the request failed
        else:
            result[cache] = (
                response.text
            )  # Record the text response if the request succeeded

    return result


@app.task
def refresh_book_cache(book_id, update_in=None):
    """
    Celery task to refresh (update) the cached data for a specific book across multiple caches.

    This function fetches the latest book data from the Taaghche API and updates the specified caches.

    Args:
        book_id (str): The unique identifier for the book.
        update_in (list, optional): A list of cache names in which to update the data.
                                    Defaults to all caches defined in settings.CACHES.

    Returns:
        dict: A dictionary with cache names as keys and the server's response as values.
              If the Taaghche API is down, returns a dictionary with an error message.
    """
    if update_in is None:
        update_in = settings.CACHES

    result = {}
    endpoint = reverse("get-book", kwargs={"book_id": book_id})
    url = f"http://django:8000{endpoint}"
    headers = {"Authorization": f"Bearer {settings.CELERY_SECRET_KEY}"}

    book = Book(book_id=book_id)
    data = json.dumps(
        book.fetch_book_data()
    )  # Fetch the latest book data from the Taaghche API

    if data:
        # Iterate through the specified caches and send a PUT request to update the cache.
        for cache in update_in:
            response = request(
                method="PUT",
                url=url,
                data={"cache": cache, "data": data},
                headers=headers,
            )
            if response.status_code != 200:
                result[cache] = (
                    response.json()
                )  # Record the JSON response if the request failed
            else:
                result[cache] = (
                    response.text
                )  # Record the text response if the request succeeded

        return result
    else:
        return {"error": "It seems Taaghche API is down!"}
