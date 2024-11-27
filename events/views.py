from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from .models import Event
from .serializers import (
    EventSerializer, 
    EventDateSerializer, 
)
from rest_framework.permissions import IsAuthenticated


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления мероприятиями.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # permission_classes = [IsAuthenticated]


class EventDatesView(generics.RetrieveAPIView):
    """
    Представление для получения всех дат конкретного мероприятия.
    
    URL: /api/events/{event_id}/dates/
    """
    queryset = Event.objects.all()
    serializer_class = EventDateSerializer
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        event_id = kwargs.get('event_id')
        try:
            event = Event.objects.get(event_id=event_id)
            dates = event.dates  # Список дат из ArrayField
            serializer = EventDateSerializer(dates, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({"error": "Мероприятие не найдено"}, status=status.HTTP_404_NOT_FOUND)
        