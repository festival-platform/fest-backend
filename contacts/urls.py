from django.urls import path
from .views import contacts_detail

urlpatterns = [
    path('', contacts_detail, name='contacts_detail'),
]