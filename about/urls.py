from django.urls import path
from .views import about_detail

urlpatterns = [
    path('', about_detail, name='about_detail'),
]