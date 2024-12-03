from rest_framework import serializers
from .models import Event, EventImage


class EventDatesSerializer(serializers.Serializer):
    """
    Сериализатор для поля dates модели Event.
    """
    dates = serializers.ListField(
        child=serializers.DateField(),
        help_text="Список доступных дат для бронирования."
    )
    


class EventImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = EventImage
        fields = ('image_url',)

    def get_image_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)

class EventSerializer(serializers.ModelSerializer):
    images = EventImageSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = (
            'event_id',
            'name',
            'description',
            'dates',
            'price',
            'capacity',
            'booked_seats',
            'images',
        )
