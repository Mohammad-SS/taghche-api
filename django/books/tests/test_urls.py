from time import sleep

import pytest
from .classes import Book
from django.urls import reverse
import requests
from django.core.cache import caches
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def test_url():
    return "http://localhost:8000"


@pytest.fixture
def test_first_book():
    return Book(book_id=30749)


@pytest.fixture
def test_second_book():
    return Book(book_id=32749)


@pytest.fixture
def test_third_book():
    return Book(book_id=25149)


def test_get_book_view(test_first_book, test_url):
    endpoint = reverse("get-book", kwargs={"book_id": test_first_book.book_id})
    url = f"{test_url}{endpoint}"
    response = requests.get(url)
    assert response.status_code == 200
    assert "book" in response.json()
    assert response.json().get("book", {}).get("id", 0) == test_first_book.book_id


def test_caches(test_first_book, test_url):
    endpoint = reverse("get-book", kwargs={"book_id": test_first_book.book_id})
    url = f"{test_url}{endpoint}"
    caches["default"].delete(test_first_book.book_id)
    caches["redis_cache"].delete(test_first_book.book_id)

    response = requests.get(url)
    print(response.headers["data-origin"])
    caches["default"].delete(test_first_book.book_id)
    sleep(2)
    response = requests.get(url)
    print(response.headers["data-origin"])
    sleep(2)
    caches["redis_cache"].delete(test_first_book.book_id)
    print(response.headers["data-origin"])

    # logger.info('This is an info message')
    # print(test_first_book.get_from_cache("default") is not None)
    # assert test_first_book.get_from_cache("default") is not None
