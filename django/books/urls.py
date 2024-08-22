from django.urls import path
from .views import GetBookData

urlpatterns = [path("api/book/<int:book_id>", GetBookData.as_view(), name="get-book")]
