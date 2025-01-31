# admin.py

from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from .models import Event, EventImage, EventDate, Booking
from .forms import EventAdminForm

class EventDateInline(admin.TabularInline):
    model = EventDate
    extra = 1
    fields = ('date', 'time_slot', 'capacity', 'booked_seats')
    readonly_fields = ('booked_seats',)

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1
    fields = ('thumbnail', 'image',)
    readonly_fields = ('thumbnail',)

    def thumbnail(self, obj):
        if obj.image and obj.image.url:
            return format_html('<img src="{}" style="max-height:100px; max-width:100px;" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = "Preview"

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    inlines = [EventDateInline, EventImageInline]
    
    list_display = ('name_en', 'morning_price', 'afternoon_price', 'evening_price')
    search_fields = ('name_en', 'name_de')
    
    fields = (
        'name_en',
        'name_de',
        'description_en',
        'description_de',
        'morning_price',
        'afternoon_price',
        'evening_price',
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id',
        'user',
        'event',
        'event_date',
        'quantity',
        'total_price',  # добавлено: метод для отображения цены
        'payment_status'
    )
    search_fields = ('user__first_name', 'user__last_name', 'event__name')
    list_editable = ('payment_status',)
    readonly_fields = ("stripe_payment_intent_id", "paypal_payment_id", "total_price")

    def total_price(self, obj):
        """
        Вычисляет общую стоимость бронирования, исходя из выбранного временного слота и количества.
        """
        if obj.event_date and obj.event:
            slot = obj.event_date.time_slot
            if slot == 'morning':
                price = obj.event.morning_price
            elif slot == 'afternoon':
                price = obj.event.afternoon_price
            elif slot == 'evening':
                price = obj.event.evening_price
            else:
                return "-"
            total = price * obj.quantity  # Умножение объектов Money поддерживается djmoney
            return total  # возвращает объект Money (например, EUR 40.00)
        return "-"

    total_price.short_description = "Цена бронирования"
