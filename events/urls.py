from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventDatesView, EventViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')


urlpatterns = [
    path('', include(router.urls)),
    path('events/<int:event_id>/dates/', EventDatesView.as_view(), name='event-dates'),
]