from rest_framework import serializers
from .models import Event, Review, EventDate

class EventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDate
        fields = ['id', 'date', 'time_slot', 'capacity', 'booked_seats']
    


class EventSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    event_dates = EventDateSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = (
            'event_id',
            'name_en',
            'name_de',
            'description_en',
            'description_de',
            'event_dates',  # Изменено
            'morning_price',
            'afternoon_price',
            'evening_price',           
            'images',
        )

    def get_images(self, obj):
        request = self.context.get('request')
        image_urls = [request.build_absolute_uri(image.image.url) for image in obj.images.all()]
        return image_urls
    

class BookingPaymentSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    event_date_id = serializers.IntegerField()  # Изменено
    quantity = serializers.IntegerField(min_value=1)
    payment_provider = serializers.ChoiceField(choices=[('stripe', 'Stripe'), ('paypal', 'PayPal')], default='stripe')

    def validate_event_date_id(self, value):
        if not EventDate.objects.filter(id=value).exists():
            raise serializers.ValidationError("Временной промежуток не существует.")
        return value
    

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['review_id', 'author', 'text', 'stars', 'event']