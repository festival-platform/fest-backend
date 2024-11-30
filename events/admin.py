from django.contrib import admin
from django.forms import ModelForm, DateInput
from .models import Event

class EventAdminForm(ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'dates': DateInput(attrs={'placeholder': 'YYYY-MM-DD'}),
        }

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
