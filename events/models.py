from django.db import models
from djmoney.models.fields import MoneyField
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from djmoney.money import Money



class User(models.Model):
    """
    Модель пользователя.

    Поля:
        user_id (AutoField): Уникальный идентификатор пользователя (автоинкремент).
        first_name (CharField): Имя пользователя.
        last_name (CharField): Фамилия пользователя.
        email (EmailField): Email пользователя (уникальный, используется для идентификации).
        phone (CharField): Номер телефона пользователя (опционально).
        booked_dates (ArrayField): Список дат, на которые пользователь уже записан.
        bookings (RelatedManager): Связанные бронирования пользователя через модель Booking.
    """
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Email пользователя. Используется для идентификации."
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Номер телефона должен быть в формате: '+999999999'. Допустимо до 15 цифр."
            )
        ],
        help_text="Номер телефона пользователя."
    )
    booked_dates = ArrayField(
        models.DateField(),
        blank=True,
        default=list,
        help_text="Список дат, на которые пользователь уже записан."
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    
    name_en = models.CharField('Name [en]', max_length=255, blank=True, null=True)
    name_de = models.CharField('Name [de]', max_length=255, blank=True, null=True)
    
    description_en = models.TextField('Description [en]', blank=True, null=True)
    description_de = models.TextField('Description [de]', blank=True, null=True)
    
    # Фиксированные цены для разных слотов
    morning_price = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency='EUR',
        default=Money(20, 'EUR'),
        help_text= "Цена для утреннего слота"
    )
    afternoon_price = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency='EUR',
        default=Money(25, 'EUR'),
        help_text="Цена для дневного слота"
    )
    evening_price = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency='EUR',
        default=Money(30, 'EUR'),
        help_text="Цена для вечернего слота"
    )

    def __str__(self):
        return self.name_en or 'No name'
    

class EventDate(models.Model):
    TIME_SLOT_CHOICES = [
        ('morning', 'Утро'),
        ('afternoon', 'День'),
        ('evening', 'Вечер'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_dates')
    date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOT_CHOICES, default='morning')
    capacity = models.PositiveIntegerField()
    booked_seats = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('event', 'date', 'time_slot')

    def __str__(self):
        return f"{self.date} ({self.get_time_slot_display()})"
    

class EventImage(models.Model):
    """
    Модель изображения мероприятия.

    Хранит изображения, связанные с конкретным мероприятием.
    
    Поля:
        event (ForeignKey): Ссылка на мероприятие, к которому относится изображение.
        image (ImageField): Поле для загрузки изображения.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='event_images/')

    def __str__(self):
        return f"Image for {self.event.name_en}"


def validate_stars(value):
    """
    Проверка, что значение stars модели Review находится в допустимом диапазоне
    """
    if value < 1 or value > 5:
        raise ValidationError('Количество звезд должно быть в диапазоне от 1 до 5.')


class Review(models.Model):
    """
    Модель отзыва.

    Представляет собой отзыв, оставленный пользователем о мероприятии.

    Поля:
        review_id (AutoField): Уникальный идентификатор отзыва (автоинкремент).
        author (CharField): Имя автора отзыва.
        text (TextField): Текст отзыва.
        stars (PositiveIntegerField): Количество звезд (оценка) отзыва.
        event (ForeignKey): Ссылка на мероприятие, к которому относится отзыв.
    """
    review_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=255)
    text = models.TextField()
    stars = models.PositiveIntegerField(validators=[validate_stars])
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')  # Добавлено поле event

    def __str__(self):
        return f"Отзыв от {self.author}"


class Booking(models.Model):
    """
    Модель бронирования.

    Связывает пользователя с мероприятием и содержит информацию о дате бронирования, статусе оплаты, 
    и количество забронированных мест.

    Поля:
        booking_id (AutoField): Уникальный идентификатор бронирования (автоинкремент).
        user (ForeignKey): Ссылка на пользователя, который сделал бронирование.
        event (ForeignKey): Ссылка на мероприятие.
        event_date (ForeignKey) : Ссылка на дату мероприятия.
        payment_status (BooleanField): Статус оплаты.
        stripe_payment_intent_id(CharField): ID платежа в Stripe.
        quantity (PositiveIntegerField): Количество забронированных мест в рамках одного бронирования.
    """
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    event_date = models.ForeignKey(EventDate, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)  # Изменено
    payment_status = models.BooleanField(default=False)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    paypal_payment_id = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user} - {self.event.name_en} on {self.event_date}"
    