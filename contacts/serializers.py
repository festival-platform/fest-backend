from rest_framework import serializers
from django.conf import settings
from .models import ContactPage

class ContactPageSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = ContactPage
        fields = (
            'id',
            'title_en',
            'title_de',
            'description_en',
            'description_de',
            'phone',
            'email',
            'address',
            'images',
        )

    def get_images(self, obj):
        request = self.context.get('request')
        return [request.build_absolute_uri(img.image.url) for img in obj.images.all()]
