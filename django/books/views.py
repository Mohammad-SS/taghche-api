import json

from rest_framework.views import APIView, Response, status
from django.conf import settings
from .classes import Book


class GetBookData(APIView):
    """
    API View for handling book-related operations.

    This class provides three main functionalities: retrieving book data, updating cached book data,
    and deleting cached book data. Each operation is handled by a separate HTTP method (GET, PUT, DELETE).
    """

    # Responses for common scenarios
    NOT_FOUND_RESPONSE = Response(
        {"error": "No book found"},
        headers={"data-origin": None},
        status=status.HTTP_404_NOT_FOUND,
    )
    NOT_ALLOWED_RESPONSE = Response(
        {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
    )

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve book data.

        Retrieves the book data either from the cache or from an upstream source if not cached.

        Args:
            request: The HTTP request object.
            *args: Additional arguments.
            **kwargs: Keyword arguments containing `book_id`.

        Returns:
            Response: A Response object containing the book data or an error message.
        """
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
        """
        Handles DELETE requests to remove book data from the cache.

        The request must be authorized with a valid secret key.

        Args:
            request: The HTTP request object containing the `cache` name in the body.
            *args: Additional arguments.
            **kwargs: Keyword arguments containing `book_id`.

        Returns:
            Response: A Response object indicating success or an error message.
        """
        if not self.is_allowed(request):
            return self.NOT_ALLOWED_RESPONSE

        book_id = kwargs.get("book_id", None)
        if not book_id:
            return self.NOT_FOUND_RESPONSE

        book = Book(book_id=book_id)
        cache_name = request.data.get("cache", None)
        if not cache_name:
            return Response(
                {"error": "cache is a required field"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = book.delete_in_cache(cache_name=cache_name)
        return Response({"success": True, "message": result})

    def put(self, request, *args, **kwargs):
        """
        Handles PUT requests to update book data in the cache.

        The request must be authorized with a valid secret key and should contain the book data.

        Args:
            request: The HTTP request object containing `data` and `cache` in the body.
            *args: Additional arguments.
            **kwargs: Keyword arguments containing `book_id`.

        Returns:
            Response: A Response object indicating success or an error message.
        """
        if not self.is_allowed(request):
            return self.NOT_ALLOWED_RESPONSE

        request_data = request.data
        cache = request.data.get("cache", None)

        try:
            data = json.loads(request_data.get("data", None))
        except json.JSONDecodeError:
            data = None

        book_id = kwargs.get("book_id", None)
        if not book_id:
            return self.NOT_FOUND_RESPONSE

        if not data:
            return Response(
                {"error": "data is a required field"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        book = Book(book_id=book_id)
        result = book.set_in_cache(cache_name=cache, value=data)
        return Response(data={"success": True, "message": result})

    def is_allowed(self, request):
        """
        Verifies if the request is authorized by checking the secret key in the headers.

        Args:
            request: The HTTP request object.

        Returns:
            bool: True if authorized, False otherwise.
        """
        secret_key = request.headers.get("Authorization")
        return secret_key == f"Bearer {settings.CELERY_SECRET_KEY}"
