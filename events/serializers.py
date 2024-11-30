from rest_framework import serializers
from .models import User, Event, Review, Booking
from djmoney.contrib.django_rest_framework.fields import MoneyField as DjMoneyMoneyField


class EventDatesSerializer(serializers.Serializer):
    """
    Сериализатор для поля dates модели Event.
    """
    dates = serializers.ListField(
        child=serializers.DateField(),
        help_text="Список доступных дат для бронирования."
    )
    