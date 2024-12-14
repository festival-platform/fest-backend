from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Админ-панель Django
    path('api/', include('events.urls')),  # Маршруты приложения 'events'
    path('api/about/', include('about.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
