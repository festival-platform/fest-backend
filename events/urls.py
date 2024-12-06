from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import get_dates, event_detail, book_event


urlpatterns = [
    path('events/<int:event_id>/book', book_event, name='book_event'),
    path('events/<int:event_id>/', event_detail, name='event_detail'),
    path('events/<int:event_id>/dates/', get_dates, name='get_dates'),
]