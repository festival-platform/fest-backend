from rest_framework import serializers
from .models import User, Event, Review, Booking
from djmoney.contrib.django_rest_framework.fields import MoneyField as DjMoneyMoneyField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'booked_dates']


class EventSerializer(serializers.ModelSerializer):
    price = DjMoneyMoneyField(max_digits=14, decimal_places=2, default_currency='EUR')

    class Meta:
        model = Event
        fields = ['event_id', 'name', 'dates', 'price', 'capacity', 'booked_seats']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['review_id', 'author', 'text', 'stars']


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['booking_id', 'user', 'event', 'date', 'payment_status']


class EventDateSerializer(serializers.Serializer):
    date = serializers.DateField()

    def to_representation(self, instance):
        """
        Переопределяем метод для сериализации даты.
        """
        return {
            'date': instance
        }
    