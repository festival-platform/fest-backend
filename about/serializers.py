# about/serializers.py

from rest_framework import serializers
from .models import AboutPage

class AboutPageSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = AboutPage
        fields = (
            'id',
            'title_en',
            'description_en',
            'title_de',
            'description_de',
            'images',
        )

    def get_images(self, obj):
        request = self.context.get('request')
        return [request.build_absolute_uri(img.image.url) for img in obj.images.all()]
    