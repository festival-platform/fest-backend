# utils/emails.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext as _

def send_booking_confirmation_email(
    recipient_email: str,
    user_name: str,
    event_name: str,
    event_date: str,  # строка, уже красиво отформатированная
    quantity: int
):
    """
    Отправляет двухъязычное (ENG + DE) письмо с деталями бронирования.
    """
    # Контекст для HTML-шаблонов
    context = {
        "user_name": user_name,
        "event_name": event_name,
        "event_date": event_date,
        "booking_quantity": quantity,
        "organizer_email": "juliesoktoberfesttours@hotmail.com",  # email организатора
    }

    # Заголовок письма (на английском)
    email_subject = _("Booking Confirmation for {event_name}").format(event_name=event_name)

    # Рендерим две разные версии HTML (ENG и DE)
    email_body_en = render_to_string("emails/booking_confirmation_en.html", context)
    email_body_de = render_to_string("emails/booking_confirmation_de.html", context)

    # Собираем их в одно HTML-письмо (можно сделать один язык — по выбору)
    combined_email_body = (
        f"<h1>{_('Thank you for your booking!')}</h1>"
        f"<p>{_('Please find below the confirmation in English and German.')}</p>"
        f"<hr><h2>English:</h2>{email_body_en}"
        f"<hr><h2>Deutsch:</h2>{email_body_de}"
    )

    # Отправка письма
    send_mail(
        subject=email_subject,
        message="",                   # Plain-text вариант (оставим пустым, мы используем html_message)
        html_message=combined_email_body,
        from_email='info@oktoberfesttour.com',
        recipient_list=[recipient_email],
        fail_silently=False,
    )


def send_organizer_notification_email(event_name: str, event_date: str, quantity: int):
    """
    Отправляет письмо организатору с информацией о новом бронировании.
    """
    subject = f"New Booking for {event_name}"
    message = (
        "Hello,\n\n"
        f"A new booking has been made.\n\n"
        f"Event: {event_name}\n"
        f"Date: {event_date}\n"
        f"Quantity: {quantity}\n\n"
        "Best regards,\n"
        "Your booking system"
    )
    
    from_email = 'info@oktoberfesttour.com'  
    recipient_list = ["juliesoktoberfesttours@hotmail.com", "s5003626@gmail.com"]
    
    send_mail(
        subject=subject,
        message=message,   
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )
