from time import sleep
import pytest
from ..classes import Book
from django.urls import reverse
import requests
import logging
from .helpers import delete_cache, refresh_caches
from django.conf import settings

# Set up logging to capture test output and warnings
logger = logging.getLogger(__name__)


# Fixtures

@pytest.fixture
def correct_book():
    """
    Fixture for a valid Book object.

    Returns:
        Book: A Book object with a valid `book_id`.
    """
    return Book(book_id=30749)


@pytest.fixture
def wrong_book():
    """
    Fixture for an invalid Book object.

    Returns:
        Book: A Book object with an invalid `book_id`.
    """
    return Book(book_id=30)


@pytest.fixture
def correct_book_url(correct_book):
    """
    Fixture for generating the correct book URL.

    Args:
        correct_book (Book): The valid Book object fixture.

    Returns:
        str: A full URL for accessing the correct book data.
    """
    endpoint = reverse("get-book", kwargs={"book_id": correct_book.book_id})
    return f"http://localhost:8000{endpoint}"


@pytest.fixture
def wrong_book_url(wrong_book):
    """
    Fixture for generating the wrong book URL.

    Args:
        wrong_book (Book): The invalid Book object fixture.

    Returns:
        str: A full URL for accessing the wrong book data.
    """
    endpoint = reverse("get-book", kwargs={"book_id": wrong_book.book_id})
    return f"http://localhost:8000{endpoint}"


# Test Cases

def test_get_correct_book_view(correct_book, correct_book_url):
    """
    Test that the correct book view returns a 200 status and the correct book data.

    Args:
        correct_book (Book): The valid Book object fixture.
        correct_book_url (str): The URL for the correct book.

    Asserts:
        - The response status code is 200.
        - The response contains the expected book data.
    """
    response = requests.get(correct_book_url)
    assert response.status_code == 200
    assert "book" in response.json()
    assert response.json().get("book", {}).get("id", 0) == correct_book.book_id


def test_get_wrong_book_view(wrong_book, wrong_book_url):
    """
    Test that the wrong book view returns a 404 status and an error message.

    Args:
        wrong_book (Book): The invalid Book object fixture.
        wrong_book_url (str): The URL for the wrong book.

    Asserts:
        - The response status code is 404.
        - The response contains an error message.
        - The `data-origin` header is 'None'.
    """
    response = requests.get(wrong_book_url)
    assert response.status_code == 404
    assert "error" in response.json()
    assert response.headers["data-origin"] == "None"


def test_caches(correct_book, correct_book_url):
    """
    Test the cache behavior by deleting and refreshing the book data cache.

    This test performs the following steps:
    1. Deletes the cache for the correct book and verifies the data is fetched from the upstream.
    2. Refreshes the caches and verifies the data is stored and retrieved from each cache in sequence.

    Args:
        correct_book (Book): The valid Book object fixture.
        correct_book_url (str): The URL for the correct book.

    Asserts:
        - The `data-origin` header is 'upstream' after cache deletion.
        - The `data-origin` header matches each cache name as the caches are refreshed.
    """
    logger.warning("Deleting Caches - wait 2 seconds!")
    delete_cache(correct_book.book_id)
    sleep(2)

    # Verify the data is fetched from the upstream source after cache deletion.
    response = requests.get(correct_book_url)
    assert response.headers["data-origin"] == "upstream"

    logger.warning("Deleting Caches - wait 2 seconds!")
    delete_cache(correct_book.book_id)
    sleep(2)

    logger.warning("Refreshing Caches - wait 2 seconds!")
    refresh_caches(correct_book.book_id)
    sleep(2)

    # Verify the data is retrieved from the first cache after refreshing.
    response = requests.get(correct_book_url)
    assert response.headers["data-origin"] == list(settings.CACHES.keys())[0]

    previous_caches = []

    # Iterate through all caches and verify the data is retrieved from each in turn.
    for cache_name in settings.CACHES:
        response = requests.get(correct_book_url)
        assert response.headers["data-origin"] == cache_name
        previous_caches.append(cache_name)

        logger.warning(f"Deleting Caches in {previous_caches} - wait 2 seconds!")
        delete_cache(correct_book.book_id, caches=previous_caches)
        sleep(2)
