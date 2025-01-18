from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AboutPage
from .serializers import AboutPageSerializer

@api_view(['GET'])
def about_detail(request):
    # Предполагаем, что у нас всегда одна запись AboutPage, либо взять первую
    about_page = AboutPage.objects.first()
    if not about_page:
        return Response({"error": "No about page content found"}, status=404)

    serializer = AboutPageSerializer(about_page, context={'request': request})
    return Response(serializer.data)
