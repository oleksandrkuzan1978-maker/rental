"""Отправка уведомлений участникам бронирования."""
import logging

from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _


def send_booking_emails(*, booking_id, subject, body, recipients,):
    """Попытаться отправить письмо каждому участнику бронирования.

        Ошибка отправки записывается в журнал.
        Отказ одного получателя не мешает попытке отправки другому.
        """
    logger = logging.getLogger(__name__)
    for recipient in recipients:
        try:
            sent = send_mail(
                subject=subject,
                message=body,
                from_email=None,
                recipient_list=[recipient],
                fail_silently=False,)
            if sent != 1:
                raise RuntimeError(_("The mail server did not accept the message."))
        except Exception:
            logger.exception("Failed to send notification. "
                                    "Booking=%s, recipient=%s",
                                booking_id,
                                        recipient,)
