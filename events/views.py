from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from .models import Event, EventDate, User, Booking
from .serializers import EventDatesSerializer, EventSerializer

import stripe
from backend.settings import STRIPE_SECRET_KEY
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Booking, EventDate, User, Event
from .serializers import BookingPaymentSerializer
from django.core.mail import send_mail  # Для отправки подтверждений (опционально)

stripe.api_key = STRIPE_SECRET_KEY # Секретный ключ Stripe

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

    dates = sorted([ed.date for ed in event.event_dates.all()])
    serializer = EventDatesSerializer({"dates": dates})
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


@api_view(['POST'])
def book_event(request, event_id):
    """
    Позволяет забронировать несколько мест на конкретную дату события.
    {
       "first_name": "Имя",
       "last_name": "Фамилия",
       "email": "уникальный@адрес.домен",
       "date": "YYYY-MM-DD",
       "quantity": 3
    }
    """
    from django.db import transaction
    from django.utils.dateparse import parse_date
    from .models import Event, EventDate, User, Booking

    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')
    date_str = request.data.get('date')
    quantity = request.data.get('quantity')

    chosen_date = parse_date(date_str)
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response({"error": "quantity должен быть числом."}, status=400)

    if not (first_name and last_name and email and chosen_date and quantity):
        return Response({"error": "Необходимо передать first_name, last_name, email, date и quantity."}, status=400)

    if quantity <= 0:
        return Response({"error": "quantity должен быть положительным."}, status=400)

    try:
        event = Event.objects.get(event_id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=404)

    # Находим конкретный EventDate
    try:
        event_date = EventDate.objects.get(event=event, date=chosen_date)
    except EventDate.DoesNotExist:
        return Response({"error": "Данная дата недоступна для выбранного события."}, status=400)

    available_seats = event_date.capacity - event_date.booked_seats
    if quantity > available_seats:
        return Response({"error": "Недостаточно свободных мест для данного количества."}, status=400)

    # Ищем или создаем пользователя
    try:
        user = User.objects.get(email=email)
        # можно обновлять данные, если хотите:
        # user.first_name = first_name
        # user.last_name = last_name
        # user.save()
    except User.DoesNotExist:
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email
        )

    with transaction.atomic():
        # Блокируем запись даты события для избежания гонок
        event_date = EventDate.objects.select_for_update().get(event=event, date=chosen_date)
        available_seats = event_date.capacity - event_date.booked_seats
        if quantity > available_seats:
            return Response({"error": "Недостаточно мест. Попробуйте другое количество."}, status=400)

        booking = Booking.objects.create(
            user=user,
            event=event,
            date=chosen_date,
            payment_status=False,  # Оплата пока не произведена
            quantity=quantity
        )
        event_date.booked_seats += quantity
        event_date.save()

    # ====== Создаем PaymentIntent в Stripe ======
    try:
        # Рассчитайте стоимость (в минимальных единицах, например, "копейках" или "центах")
        price_in_cents = int(event.price.amount * 100)
        total_amount = price_in_cents * quantity

        # Создаем PaymentIntent
        payment_intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency='eur',
            # автоматические методы оплаты
            automatic_payment_methods={'enabled': True},
        )

        # Сохраняем ID платежа в Booking (рекомендуется)
        booking.stripe_payment_intent_id = payment_intent["id"]
        booking.save()

        client_secret = payment_intent["client_secret"]
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    return Response({
        "message": "Вы успешно забронировали места на событие.",
        "booking_id": booking.booking_id,
        "event_id": event.event_id,
        "date": chosen_date.strftime("%Y-%m-%d"),
        "quantity": quantity,
        "payment_status": booking.payment_status,
        "client_secret": client_secret  # Возвращаем клиенту для завершения оплаты
    }, status=201)
