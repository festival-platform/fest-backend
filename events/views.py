from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from .models import Event, EventDate, User, Booking
from .serializers import EventDatesSerializer, EventSerializer

import stripe
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Booking, EventDate, User, Event
from .serializers import BookingPaymentSerializer
from django.core.mail import send_mail  # Для отправки подтверждений (опционально)


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
       "date": "YYYY-MM-DD",
       "quantity": 3
    }
    """
    from django.db import transaction
    from django.utils.dateparse import parse_date
    from .models import Event, EventDate, User, Booking

    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    date_str = request.data.get('date')
    quantity = request.data.get('quantity')

    chosen_date = parse_date(date_str)
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response({"error": "quantity должен быть числом."}, status=400)

    if not (first_name and last_name and chosen_date and quantity):
        return Response({"error": "Необходимо передать first_name, last_name, date и quantity."}, status=400)
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

    # Создаём пользователя (как заказчика)
    user = User.objects.create(
        first_name=first_name,
        last_name=last_name
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

    return Response({
        "message": "Вы успешно забронировали места на событие.",
        "booking_id": booking.booking_id,
        "event_id": event.event_id,
        "date": chosen_date.strftime("%Y-%m-%d"),
        "quantity": quantity,
        "payment_status": booking.payment_status
    }, status=201)


@api_view(['POST'])
def create_booking_payment(request):
    """
    Создаёт бронирование и создаёт PaymentIntent для оплаты.
    {
        "first_name": "Имя",
        "last_name": "Фамилия",
        "email": "email@example.com",
        "phone": "1234567890",
        "event_id": 1,
        "date": "2024-10-20",
        "quantity": 3
    }
    """
    serializer = BookingPaymentSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        first_name = data['first_name']
        last_name = data['last_name']
        email = data['email']
        phone = data.get('phone', '')
        event_id = data['event_id']
        date = data['date']
        quantity = data['quantity']

        try:
            event = Event.objects.get(id=event_id)
            event_date = EventDate.objects.get(event=event, date=date)
        except (Event.DoesNotExist, EventDate.DoesNotExist):
            return Response({"error": "Мероприятие или дата не найдены."}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка доступности мест
        if event_date.booked_seats + quantity > event_date.capacity:
            return Response({"error": "Недостаточно свободных мест."}, status=status.HTTP_400_BAD_REQUEST)

        # Рассчёт общей суммы в центах
        total_amount = int(event.price.amount * quantity * 100)  # Предполагается, что price хранится в евро

        with transaction.atomic():
            # Создание или получение пользователя
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone
                }
            )
            if not created:
                # Обновляем информацию пользователя, если необходимо
                user.first_name = first_name
                user.last_name = last_name
                if phone:
                    user.phone = phone
                user.save()

            # Создание бронирования с payment_status=False
            booking = Booking.objects.create(
                user=user,
                event=event,
                date=date,
                quantity=quantity,
                payment_status=False,
            )

            # Создание PaymentIntent
            try:
                intent = stripe.PaymentIntent.create(
                    amount=total_amount,
                    currency=event.price.currency.lower(),
                    metadata={'booking_id': booking.id},
                    automatic_payment_methods={'enabled': True},
                )
            except Exception as e:
                booking.delete()  # Отмена бронирования при ошибке создания PaymentIntent
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'clientSecret': intent['client_secret'],
                'booking_id': booking.id
            }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def stripe_webhook(request):
    """
    Обрабатывает вебхуки от Stripe.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Добавь этот секрет в settings.py

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # Некорректный payload
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        # Некорректная подпись
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Обработка события
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        booking_id = payment_intent['metadata'].get('booking_id')

        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                booking.payment_status = True
                booking.save()

                # Обновление забронированных мест
                event_date = EventDate.objects.get(event=booking.event, date=booking.date)
                event_date.booked_seats += booking.quantity
                event_date.save()

                # (Опционально) Отправка подтверждения по email
                send_mail(
                    'Подтверждение бронирования',
                    f'Здравствуйте, {booking.user.first_name}!\n\nВаше бронирование на мероприятие "{booking.event.name}" на дату {booking.date} успешно оплачено.',
                    'from@example.com',  # Замените на ваш email
                    [booking.user.email],
                    fail_silently=False,
                )
            except Booking.DoesNotExist:
                pass
            except EventDate.DoesNotExist:
                pass

    return Response(status=status.HTTP_200_OK)
