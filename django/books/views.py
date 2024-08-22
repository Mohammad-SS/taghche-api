from rest_framework.views import APIView, Response, status
from django.conf import settings
from .classes import Book


class GetBookData(APIView):
    NOT_FOUND_RESPONSE = Response({"error": "No book found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("book_id", None)
        if not book_id:
            print("No book_id is provided")
            return self.NOT_FOUND_RESPONSE

        book = Book(book_id=book_id)

        data = book.get_cached_data()

        if not data:
            print("Didnt Find in caches ... getting from API")
            data = book.fetch_book_data()

        if not data:
            print("didnt find from API")
            return self.NOT_FOUND_RESPONSE

        return Response(data=data)

    def delete(self, request, *args, **kwargs):
        secret_key = request.headers.get('Authorization')

        # Check if the API key matches the expected value
        if secret_key != f'Bearer {settings.CELERY_SECRET_KEY}':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        book_id = kwargs.get("book_id", None)
        if not book_id:
            return self.NOT_FOUND_RESPONSE

        book = Book(book_id=book_id)
        cache_name = request.data.get("cache", None)
        if not cache_name:
            return Response({'error': 'cache is required field'}, status=status.HTTP_400_BAD_REQUEST)
        result = book.delete_in_cache(cache_name=cache_name)
        return Response({'success': True, "message": result})
