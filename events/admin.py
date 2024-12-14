from django.contrib import admin
from django.forms import ModelForm
from django.utils.html import format_html
from .models import Event, EventImage, EventDate, Booking


class EventAdminForm(ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        # Можно добавить виджеты, если нужно кастомизировать


class EventDateInline(admin.TabularInline):
    model = EventDate
    extra = 1


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
    list_display = ('name', 'price')
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Отображаем поля бронирования в списке
    list_display = (
        'booking_id',
        'user',         # показывает пользователя, сделавшего бронирование
        'event',        # показывает мероприятие
        'date',         # на какую дату забронировали
        'quantity',     # сколько мест забронировано
        'payment_status'
    )
    
    # Поиск по имени и фамилии пользователя и названию события
    search_fields = ('user__first_name', 'user__last_name', 'event__name')
    
    # Поля для редактирования прямо из списка, если нужно
    list_editable = ('payment_status',)
