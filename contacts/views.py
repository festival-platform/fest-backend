from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ContactPage
from .serializers import ContactPageSerializer

@api_view(['GET'])
def contacts_detail(request):
    contact_page = ContactPage.objects.first()
    if not contact_page:
        return Response({"error": "No contact page content found"}, status=404)

    serializer = ContactPageSerializer(contact_page, context={'request': request})
    return Response(serializer.data)
