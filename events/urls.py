from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import get_dates


urlpatterns = [
    path('events/<int:event_id>/dates/', get_dates, name='get_dates'),
]