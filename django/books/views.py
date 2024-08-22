import json

from rest_framework.views import APIView, Response, status
from django.conf import settings
from .classes import Book


class GetBookData(APIView):
    NOT_FOUND_RESPONSE = Response({"error": "No book found"}, headers={"data-origin": None},
                                  status=status.HTTP_404_NOT_FOUND)
    NOT_ALLOWED_RESPONSE = Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("book_id", None)
        if not book_id:
            return self.NOT_FOUND_RESPONSE

        book = Book(book_id=book_id)

        data, place = book.get_data()
        if data:
            return Response(data=data, headers={"data-origin": place})
        else:
            return self.NOT_FOUND_RESPONSE

    def delete(self, request, *args, **kwargs):
        if not self.is_allowed(request):
            return self.NOT_ALLOWED_RESPONSE
        book_id = kwargs.get("book_id", None)
        if not book_id:
            return self.NOT_FOUND_RESPONSE

        book = Book(book_id=book_id)
        cache_name = request.data.get("cache", None)
        if not cache_name:
            return Response({'error': 'cache is required field'}, status=status.HTTP_400_BAD_REQUEST)
        result = book.delete_in_cache(cache_name=cache_name)
        return Response({'success': True, "message": result})

    def put(self, request, *args, **kwargs):
        if not self.is_allowed(request):
            return self.NOT_ALLOWED_RESPONSE
        request_data = request.data
        cache = request.data.get("cache", None)
        try:
            data = json.loads(request_data.get("data", None))
        except:
            data = None

        book_id = kwargs.get("book_id", None)
        if not book_id:
            return self.NOT_FOUND_RESPONSE

        if not data:
            return Response({'error': 'data is required field'}, status=status.HTTP_400_BAD_REQUEST)

        book = Book(book_id=book_id)
        result = book.set_in_cache(cache_name=cache, value=data)
        return Response(data={'success': True, "message": result})

    def is_allowed(self, request):
        secret_key = request.headers.get('Authorization')
        if secret_key != f'Bearer {settings.CELERY_SECRET_KEY}':
            return False
        return True
