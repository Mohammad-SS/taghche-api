import requests
from django.conf import settings
from django.core.cache import caches


class Book:
    def __init__(self, book_id, cache_names=None):
        self.book_id = book_id
        self.caches = cache_names
        if self.caches is None:
            self.caches = settings.CACHES

    def fetch_book_data(self):
        # Interact with the Taaghche API
        url = f"https://get.taaghche.com/v2/book/{self.book_id}/"
        response = requests.request("GET", url, headers={'User-Agent': 'TaagcheApplication/1.0', "accepts": "*/*"})

        if response.status_code == 200:
            data = response.json()
            self.set_cached_data(data)

            return data
        return None

    def get_cached_data(self):
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
        result = {}
        for cache_name in self.caches:
            result[cache_name] = self.set_in_cache(cache_name, value)
        return result

    def get_from_cache(self, cache_name):
        cache = caches[cache_name]
        data = cache.get(self.book_id)
        if data is not None:
            return data

        return None

    def set_in_cache(self, cache_name, value):
        cache = caches[cache_name]
        cache.set(self.book_id, value)
        if cache.get(self.book_id):
            return f"Data for {self.book_id} set in {cache_name} cache"
        return f"Data for {self.book_id} not set in {cache_name} cache"

    def delete_in_cache(self, cache_name):
        cache = caches[cache_name]
        if cache.get(self.book_id) is not None:
            cache.delete(self.book_id)
            return f"Deleted data in {cache_name} cache"
        else:
            return f"Cache not found in {cache_name} cache"

    def get_data(self):
        data, place = self.get_cached_data()
        if not data:
            data = self.fetch_book_data()
            if data:
                place = "upstream"
        return data, place
