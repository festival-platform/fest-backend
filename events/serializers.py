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
    

class EventSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

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

    def get_images(self, obj):
        request = self.context.get('request')
        image_urls = [request.build_absolute_uri(image.image.url) for image in obj.images.all()]
        return image_urls
    