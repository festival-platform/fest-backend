from django.contrib import admin
from django.forms import ModelForm, DateInput
from .models import Event, EventImage

class EventAdminForm(ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'dates': DateInput(attrs={'placeholder': 'YYYY-MM-DD'}),
        }

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    inlines = [EventImageInline]
    list_display = ('name', 'price', 'capacity')
    search_fields = ('name',)
    list_filter = ('dates',)
    