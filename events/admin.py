from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'name', 'price', 'capacity', 'booked_seats')
    search_fields = ('name',)
    list_filter = ('dates',)
    