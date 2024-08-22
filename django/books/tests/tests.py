from time import sleep

import pytest
from ..classes import Book
from django.urls import reverse
import requests
import logging
from .helpers import delete_cache, refresh_caches
from django.conf import settings

logger = logging.getLogger(__name__)


@pytest.fixture
def first_book():
    return Book(book_id=30749)


@pytest.fixture
def url(first_book):
    endpoint = reverse("get-book", kwargs={"book_id": first_book.book_id})
    return f"http://localhost:8000{endpoint}"


def test_get_book_view(first_book, url):
    response = requests.get(url)
    assert response.status_code == 200
    assert "book" in response.json()
    assert response.json().get("book", {}).get("id", 0) == first_book.book_id


def test_caches(first_book, url):
    logger.warning("Deleting Caches - wait 2 seconds !")
    delete_cache(first_book.book_id)
    sleep(2)
    response = requests.get(url)
    assert response.headers["data-origin"] == "upstream"
    logger.warning("Deleting Caches - wait 2 seconds !")
    delete_cache(first_book.book_id)
    sleep(2)
    logger.warning("Refreshing Caches - wait 2 seconds !")
    refresh_caches(first_book.book_id)
    sleep(2)
    response = requests.get(url)
    assert response.headers["data-origin"] == list(settings.CACHES.keys())[0]

    for cache_name in settings.CACHES:
        previous_caches = []
        response = requests.get(url)
        assert response.headers["data-origin"] == cache_name
        previous_caches.append(cache_name)
        logger.warning(f"Deleting Caches in {previous_caches} - wait 2 seconds !")
        delete_cache(first_book.book_id, caches=previous_caches)
        sleep(2)
