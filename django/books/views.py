import requests
from django.core.cache import caches
from rest_framework.views import APIView, Response


class GetBookData(APIView):
    NOT_FOUND_RESPONSE = Response({"error": "No book found"}, status=404)
    CACHES = ("default", "redis_cache")

    def get(self, request, *args, **kwargs):
        self.book_id = kwargs.get("book_id", None)
        if not self.book_id:
            print("No book_id is provided")
            return self.NOT_FOUND_RESPONSE

        data = self.get_cached_data()

        if not data:
            print("Didnt Find in caches ... getting from API")
            data = self.fetch_book_data()

        if not data:
            print("didnt find from API")
            return self.NOT_FOUND_RESPONSE

        return Response(data=data)

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
        # Attempt to get data from the caches
        for cache_name in self.CACHES:
            data = self.get_from_cache(cache_name)
            if data:
                return data

        return None

    def set_cached_data(self, value):
        for cache_name in self.CACHES:
            self.set_in_cache(cache_name, value)

    def get_from_cache(self, cache_name):
        cache = caches[cache_name]
        data = cache.get(self.book_id)
        if data is not None:
            print(f"Data found in {cache_name} cache")
            return data

        return None

    def set_in_cache(self, cache_name, value):
        cache = caches[cache_name]
        cache.set(self.book_id, value)
        print(f"Fetched data set in {cache_name} cache")
