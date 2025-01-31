from django import forms
from .models import Event

class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'name_en',
            'name_de',
            'description_en',
            'description_de',
            'morning_price',
            'afternoon_price',
            'evening_price',
        ]