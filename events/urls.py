from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import get_dates, event_detail, book_event, create_review, list_reviews, stripe_webhook


urlpatterns = [
    path('events/<int:event_id>/book', book_event, name='book_event'),
    path('events/<int:event_id>/', event_detail, name='event_detail'),
    path('events/<int:event_id>/dates/', get_dates, name='get_dates'),
    path('reviews/', list_reviews, name='list_reviews'),
    path('reviews/create/', create_review, name='create_review'),
    path('events/<int:event_id>/reviews/', list_reviews, name='list_reviews_by_event'),
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
]
