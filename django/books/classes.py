import requests
from django.conf import settings
from django.core.cache import caches


class Book:
    """
    A class representing a book and its related caching mechanisms.

    This class interacts with external APIs to fetch book data and manages caching across multiple caches.
    """

    def __init__(self, book_id, cache_names=None):
        """
        Initializes a Book object with a given book ID and optional cache names.

        Args:
            book_id (str): The unique identifier for the book.
            cache_names (list, optional): A list of cache names. Defaults to None, which uses the settings-defined caches.
        """
        self.book_id = book_id
        self.caches = cache_names if cache_names is not None else settings.CACHES

    def fetch_book_data(self):
        """
        Fetches book data from the Taaghche API.

        This method sends a GET request to the Taaghche API to retrieve book data and caches it.

        Returns:
            dict: The book data if successfully fetched, None otherwise.
        """
        url = f"https://get.taaghche.com/v2/book/{self.book_id}/"
        response = requests.get(
            url, headers={"User-Agent": "TaaghcheApplication/1.0", "accepts": "*/*"}
        )

        if response.status_code == 200:
            data = response.json()
            self.set_cached_data(data)
            return data

        return None

    def get_cached_data(self):
        """
        Retrieves the book data from the caches.

        It checks each cache for the book data and if found, it returns the data and the cache name.
        If the data is missing in a cache, it ensures that the data is set in all previously missed caches.

        Returns:
            tuple: A tuple containing the book data and the cache name it was found in, or (None, None) if not found.
        """
        missing_cache = []
        for cache_name in self.caches:
            data = self.get_from_cache(cache_name)
            if data:
                for cache in missing_cache:
                    self.set_in_cache(cache, data)
                return data, cache_name
            missing_cache.append(cache_name)

        return None, None

    def set_cached_data(self, value):
        """
        Sets the book data in all specified caches.

        Args:
            value (dict): The book data to be cached.

        Returns:
            dict: A dictionary indicating success for each cache.
        """
        result = {}
        for cache_name in self.caches:
            result[cache_name] = self.set_in_cache(cache_name, value)
        return result

    def get_from_cache(self, cache_name):
        """
        Retrieves the book data from a specific cache.

        Args:
            cache_name (str): The name of the cache to retrieve data from.

        Returns:
            dict: The book data if found, None otherwise.
        """
        cache = caches[cache_name]
        data = cache.get(self.book_id)
        return data if data is not None else None

    def set_in_cache(self, cache_name, value):
        """
        Sets the book data in a specific cache.

        Args:
            cache_name (str): The name of the cache to set data in.
            value (dict): The book data to be cached.

        Returns:
            str: A message indicating whether the data was successfully set or not.
        """
        cache = caches[cache_name]
        cache.set(self.book_id, value)
        if cache.get(self.book_id):
            return f"Data for {self.book_id} set in {cache_name} cache"
        return f"Data for {self.book_id} not set in {cache_name} cache"

    def delete_in_cache(self, cache_name):
        """
        Deletes the book data from a specific cache.

        Args:
            cache_name (str): The name of the cache to delete data from.

        Returns:
            str: A message indicating whether the data was successfully deleted or not.
        """
        cache = caches[cache_name]
        if cache.get(self.book_id) is not None:
            cache.delete(self.book_id)
            return f"Deleted data in {cache_name} cache"
        else:
            return f"Cache not found in {cache_name} cache"

    def get_data(self):
        """
        Retrieves the book data, first attempting to get it from the cache, and if not found, fetching it from the API.

        Returns:
            tuple: A tuple containing the book data and the source of the data ("upstream" or cache name).
        """
        data, place = self.get_cached_data()
        if not data:
            data = self.fetch_book_data()
            if data:
                place = "upstream"
        return data, place
