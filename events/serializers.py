from rest_framework import serializers
from .models import Event

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
    dates = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'event_id',
            'name_en',
            'name_de',
            'description_en',
            'description_de',
            'dates',
            'price',
            'images',
        )

    def get_images(self, obj):
        request = self.context.get('request')
        image_urls = [request.build_absolute_uri(image.image.url) for image in obj.images.all()]
        return image_urls

    def get_dates(self, obj):
        return sorted([ed.date.strftime("%Y-%m-%d") for ed in obj.event_dates.all()])
    

class BookingPaymentSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    event_id = serializers.IntegerField()
    date = serializers.DateField()
    quantity = serializers.IntegerField(min_value=1)
    # email = serializers.EmailField()  # Добавляем email для связи с пользователем (опционально)
    # phone = serializers.CharField(max_length=20, required=False)  # Добавляем телефон (опционально)

    def validate_event_id(self, value):
        if not Event.objects.filter(id=value).exists():
            raise serializers.ValidationError("Мероприятие не существует.")
        return value

    def validate_date(self, value):
        # Дополнительная валидация даты, если необходимо
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество человек должно быть хотя бы 1.")
        return value
