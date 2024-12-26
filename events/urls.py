from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import get_dates, event_detail, book_event, create_booking_payment, stripe_webhook


urlpatterns = [
    path('events/<int:event_id>/book', book_event, name='book_event'),
    path('events/<int:event_id>/', event_detail, name='event_detail'),
    path('events/<int:event_id>/dates/', get_dates, name='get_dates'),
    path('api/create-booking-payment/', create_booking_payment, name='create-booking-payment'),
    path('api/webhook/', stripe_webhook, name='stripe-webhook'),
]
