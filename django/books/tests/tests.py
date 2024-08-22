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
def correct_book():
    return Book(book_id=30749)


@pytest.fixture
def wrong_book():
    return Book(book_id=30)


@pytest.fixture
def correct_book_url(correct_book):
    endpoint = reverse("get-book", kwargs={"book_id": correct_book.book_id})
    return f"http://localhost:8000{endpoint}"


@pytest.fixture
def wrong_book_url(wrong_book):
    endpoint = reverse("get-book", kwargs={"book_id": wrong_book.book_id})
    return f"http://localhost:8000{endpoint}"


def test_get_correct_book_view(correct_book, correct_book_url):
    response = requests.get(correct_book_url)
    assert response.status_code == 200
    assert "book" in response.json()
    assert response.json().get("book", {}).get("id", 0) == correct_book.book_id


def test_get_wrong_book_view(wrong_book, wrong_book_url):
    response = requests.get(wrong_book_url)
    assert response.status_code == 404
    assert "error" in response.json()
    assert response.headers["data-origin"] == "None"


def test_caches(correct_book, correct_book_url):
    logger.warning("Deleting Caches - wait 2 seconds !")
    delete_cache(correct_book.book_id)
    sleep(2)
    response = requests.get(correct_book_url)
    assert response.headers["data-origin"] == "upstream"
    logger.warning("Deleting Caches - wait 2 seconds !")
    delete_cache(correct_book.book_id)
    sleep(2)
    logger.warning("Refreshing Caches - wait 2 seconds !")
    refresh_caches(correct_book.book_id)
    sleep(2)
    response = requests.get(correct_book_url)
    assert response.headers["data-origin"] == list(settings.CACHES.keys())[0]

    for cache_name in settings.CACHES:
        previous_caches = []
        response = requests.get(correct_book_url)
        assert response.headers["data-origin"] == cache_name
        previous_caches.append(cache_name)
        logger.warning(f"Deleting Caches in {previous_caches} - wait 2 seconds !")
        delete_cache(correct_book.book_id, caches=previous_caches)
        sleep(2)
