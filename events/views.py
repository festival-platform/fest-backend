from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Event, Review
from .serializers import EventDateSerializer, EventSerializer, ReviewSerializer, BookingPaymentSerializer
from events.utils import send_booking_confirmation_email, send_organizer_notification_email

import stripe
from backend.settings import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, paypalrestsdk
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail  # Для отправки подтверждений (опционально)
from django.db import IntegrityError, DatabaseError

stripe.api_key = STRIPE_SECRET_KEY # Секретный ключ Stripe

@api_view(["GET"])
def get_dates(request, event_id):
    """
    Выдает все EventDate на определенный Event.
    URL: /api/events/{event_id}/dates/
    """
    try:
        event = Event.objects.get(event_id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=404)

    event_dates = event.event_dates.all().order_by('date', 'time_slot')
    serializer = EventDateSerializer(event_dates, many=True)
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
def create_review(request):
    """
    Создаёт новый отзыв.
    {
        "author": "Имя автора",
        "text": "Текст отзыва",
        "stars": 5,
        "event": 1
    }
    """
    try:
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Автоматически вызывает ValidationError
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except IntegrityError as ie:
        # Ошибки целостности базы данных
        return Response({'error': 'Ошибка целостности данных: ' + str(ie)}, status=status.HTTP_400_BAD_REQUEST)
    except DatabaseError as de:
        # Общие ошибки базы данных
        return Response({'error': 'Ошибка базы данных: ' + str(de)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        # Все прочие исключения
        return Response({'error': 'Неизвестная ошибка: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_reviews(request, event_id=None):
    """
    Возвращает список всех отзывов или отзывов для конкретного мероприятия.
    """
    try:
        if event_id:
            reviews = Review.objects.filter(event__event_id=event_id)
        else:
            reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except DatabaseError as de:
        return Response({'error': 'Ошибка базы данных: ' + str(de)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': 'Неизвестная ошибка: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def book_event(request, event_id):
    """
    Позволяет забронировать несколько мест на конкретный временной слот мероприятия.
    Ожидаемый JSON:
    {
       "first_name": "Имя",
       "last_name": "Фамилия",
       "email": "уникальный@адрес.домен",
       "event_date_id": 19,
       "quantity": 3,
       "payment_provider": "stripe"  # или "paypal"
    }
    """
    from django.db import transaction
    from .models import Event, EventDate, User, Booking

    # Получаем данные из запроса через сериализатор (он уже проверяет наличие event_date_id)
    from .serializers import BookingPaymentSerializer
    serializer = BookingPaymentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    data = serializer.validated_data

    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    event_date_id = data['event_date_id']
    quantity = data['quantity']
    payment_provider = data.get('payment_provider', 'stripe')

    if quantity <= 0:
        return Response({"error": "quantity должен быть положительным."}, status=400)

    # Находим событие по event_id
    try:
        event = Event.objects.get(event_id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=404)

    # Находим конкретный временной слот (EventDate) по переданному event_date_id и привязываем его к событию
    try:
        event_date = EventDate.objects.get(id=event_date_id, event=event)
    except EventDate.DoesNotExist:
        return Response({"error": "Временной промежуток недоступен для выбранного события."}, status=400)

    available_seats = event_date.capacity - event_date.booked_seats
    if quantity > available_seats:
        return Response({"error": "Недостаточно свободных мест для данного количества."}, status=400)

    # Ищем или создаем пользователя
    try:
        user = User.objects.get(email=email)
        # При необходимости можно обновлять имя и фамилию:
        user.first_name = first_name
        user.last_name = last_name
        user.save()
    except User.DoesNotExist:
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email
        )

    with transaction.atomic():
        # Блокируем запись выбранного временного слота для избежания гонок
        event_date = EventDate.objects.select_for_update().get(id=event_date_id, event=event)
        available_seats = event_date.capacity - event_date.booked_seats
        if quantity > available_seats:
            return Response({"error": "Недостаточно мест. Попробуйте другое количество."}, status=400)

        # Создаем бронирование с привязкой к конкретному временному слоту
        booking = Booking.objects.create(
            user=user,
            event=event,
            event_date=event_date,
            payment_status=False,
            quantity=quantity
        )
        event_date.booked_seats += quantity
        event_date.save()

    # Определяем цену в зависимости от временного слота
    if event_date.time_slot == 'morning':
        slot_price = event.morning_price
    elif event_date.time_slot == 'afternoon':
        slot_price = event.afternoon_price
    elif event_date.time_slot == 'evening':
        slot_price = event.evening_price
    else:
        return Response({"error": "Неверный временной слот."}, status=400)

    price_in_cents = int(slot_price.amount * 100)
    total_amount_cents = price_in_cents * quantity
    total_amount_eur = total_amount_cents / 100.0  # Для передачи в платёжные системы (например, строка "12.34")

    # Генерируем платёж в зависимости от выбранного провайдера
    if payment_provider == 'stripe':
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=total_amount_cents,
                currency='eur',
                automatic_payment_methods={'enabled': True},
            )
            booking.stripe_payment_intent_id = payment_intent["id"]
            booking.save()

            client_secret = payment_intent["client_secret"]
            return Response({
                "message": "Вы успешно забронировали места (Stripe).",
                "booking_id": booking.booking_id,
                "event_id": event.event_id,
                "event_date_id": event_date.id,
                "quantity": quantity,
                "payment_status": booking.payment_status,
                "payment_provider": "stripe",
                "client_secret": client_secret
            }, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

    elif payment_provider == 'paypal':
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "https://example.com/paypal/return",
                "cancel_url": "https://example.com/paypal/cancel"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": event.name_en or event.name_de,
                        "sku": str(event.event_id),
                        "price": f"{total_amount_eur:.2f}",
                        "currency": "EUR",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": f"{total_amount_eur:.2f}",
                    "currency": "EUR"
                },
                "description": f"Booking for event {event.name_en or event.name_de}"
            }]
        })

        if payment.create():
            approval_url = next(
                (link.href for link in payment.links if link.method == "REDIRECT" and link.rel == "approval_url"),
                None
            )
            booking.paypal_payment_id = payment.id
            booking.save()

            if approval_url:
                return Response({
                    "message": "Вы успешно забронировали места (PayPal).",
                    "booking_id": booking.booking_id,
                    "event_id": event.event_id,
                    "event_date_id": event_date.id,
                    "quantity": quantity,
                    "payment_status": booking.payment_status,
                    "payment_provider": "paypal",
                    "approval_url": approval_url
                }, status=201)
            else:
                return Response({"error": "Не удалось получить approval_url от PayPal."}, status=400)
        else:
            return Response({"error": payment.error}, status=400)

    else:
        return Response({"error": "Неверный payment_provider"}, status=400)
    

# @csrf_exempt
@api_view(["POST"])
def stripe_webhook(request):
    """
    Эндпоинт для приёма уведомлений (webhook) от Stripe в тестовом/боевом режиме.
    """
    from .models import Booking

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        # Проверяем подпись, чтобы убедиться, что событие пришло действительно от Stripe
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

    # Обрабатываем тип события (event["type"])
    event_type = event["type"]
    data_object = event["data"]["object"]  # Основной объект в событии

    if event_type == "payment_intent.succeeded":
        payment_intent_id = data_object["id"]
        try:
            booking = Booking.objects.get(stripe_payment_intent_id=payment_intent_id)
            booking.payment_status = True
            booking.save()
            
            # Отправляем письма
            send_booking_confirmation_email(
                recipient_email=booking.user.email,
                user_name=f"{booking.user.first_name} {booking.user.last_name}",
                event_name=booking.event.name,
                event_date=booking.date.strftime("%d %B %Y"),  # Пример: 01 January 2025
                quantity=booking.quantity
            )
            send_organizer_notification_email(
                event_name=booking.event.name,
                event_date=booking.date.strftime("%d %B %Y"),
                quantity=booking.quantity
            )

        except Booking.DoesNotExist:
            # Если почему-то не нашли Booking, можно залогировать
            print("не нашелся букинг")
            pass

    elif event_type == "payment_intent.payment_failed":
        payment_intent_id = data_object["id"]
        print("неудача")

        # Аналогично: можно найти booking, зафиксировать ошибку, уведомить пользователя и т.п.

    # Можно обработать и другие события (refund, partial payment и т.д.)

    # Возвращаем 200 OK, чтобы Stripe понял, что мы приняли событие
    return Response(status=status.HTTP_200_OK)

