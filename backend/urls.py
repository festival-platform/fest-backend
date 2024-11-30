from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Админ-панель Django
    path('api/', include('events.urls')),  # Маршруты приложения 'events'
]