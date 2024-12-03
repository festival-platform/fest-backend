from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Event
from .serializers import (
    EventDatesSerializer, 
    EventSerializer
)    

@api_view(["GET"])
def get_dates(request, event_id):
    """
    Выдает все даты на определенный Event.

    URL: /api/events/{event_id}/dates/
    """
    try:
        event = Event.objects.get(event_id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=404)

    # Используем сериализатор для возвращения данных
    serializer = EventDatesSerializer({"dates": event.dates})
    return Response(serializer.data)


@api_view(['GET'])
def event_detail(request, event_id):
    """
    Выдает основную информацию о мероприятии, включая изображения.

    URL: /api/events/{event_id}/
    """
    try:
        event = Event.objects.get(event_id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=404)

    serializer = EventSerializer(event, context={'request': request})
    return Response(serializer.data)
