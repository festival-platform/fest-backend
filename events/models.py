from django.db import models
from django.contrib.auth.models import AbstractUser
from djmoney.models.fields import MoneyField
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    Модель пользователя.

    Наследуется от AbstractUser и расширяет стандартные поля пользователя.

    Поля:
        user_id (AutoField): Уникальный идентификатор пользователя (автоинкремент).
        first_name (CharField): Имя пользователя.
        last_name (CharField): Фамилия пользователя.
        booked_dates (ArrayField): Список дат, на которые пользователь уже записан.
        bookings (RelatedManager): Связанные бронирования пользователя через модель Booking.
    """
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    booked_dates = ArrayField(
        models.DateField(),
        blank=True,
        default=list,
        help_text="Список дат, на которые пользователь уже записан."
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Event(models.Model):
    """
    Модель мероприятия.

    Представляет собой событие, на которое пользователи могут бронировать места.

    Поля:
        event_id (AutoField): Уникальный идентификатор мероприятия (автоинкремент).
        name (CharField): Название мероприятия.
        dates (ArrayField): Список доступных дат для бронирования.
        price (MoneyField): Цена за участие в мероприятии.
        capacity (PositiveIntegerField): Общая вместимость мероприятия.
        booked_seats (PositiveIntegerField): Количество уже забронированных мест.
    """
    event_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    dates = ArrayField(
        models.DateField(),
        blank=True,
        default=list,
        help_text="Список доступных дат для бронирования."
    )
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='EUR')
    capacity = models.PositiveIntegerField()
    booked_seats = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


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
    """
    review_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=255)
    text = models.TextField()
    stars = models.PositiveIntegerField(validators=[validate_stars])

    def __str__(self):
        return f"Отзыв от {self.author}"


class Booking(models.Model):
    """
    Модель бронирования.

    Связывает пользователя с мероприятием и содержит информацию о дате бронирования и статусе оплаты.

    Поля:
        booking_id (AutoField): Уникальный идентификатор бронирования (автоинкремент).
        user (ForeignKey): Ссылка на пользователя, который сделал бронирование.
        event (ForeignKey): Ссылка на мероприятие, на которое сделано бронирование.
        date (DateField): Дата мероприятия, на которую сделано бронирование.
        payment_status (BooleanField): Статус оплаты бронирования (True - оплачено, False - не оплачено).
    """
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.event.name} on {self.date}"
    