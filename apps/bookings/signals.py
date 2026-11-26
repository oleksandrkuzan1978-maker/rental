"""Уведомления о создании заявки и изменении её статуса."""
from functools import partial

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Booking
from .utils.choices import Status
from .utils.notifications import send_booking_emails

@receiver(pre_save, sender=Booking, dispatch_uid="bookings.remember_status_for_email",)
def remember_status(sender, instance, using, raw=False, update_fields=None, **kwargs):
    """Определить, изменяется ли статус перед сохранением."""
    instance._email_status_changed = False
    if raw:
        return
    if update_fields is not None and "status" not in update_fields:
        return

    previous_status = (sender.objects.using(using).filter(pk=instance.pk)
                       .values_list("status", flat=True).first())

    instance._email_status_changed = (previous_status != instance.status)


@receiver(post_save, sender=Booking, dispatch_uid="bookings.send_status_email",)
def schedule_status_email(sender, instance, created, using, raw=False, **kwargs):
    """Отправить уведомления после успешной фиксации транзакции."""
    if raw:
        return

    status_changed = getattr(instance, "_email_status_changed", False)
    if not created and not status_changed:
        return

    if instance.status not in (
        Status.PENDING,
        Status.CONFIRMED,
        Status.REJECTED,
        Status.CANCELLED,
    ):
        return

    booking = (sender.objects.using(using)
               .select_related("user", "listing__user")
               .get(pk=instance.pk))

    subject = f"Booking — {booking.get_status_display()}"

    body =  (
        f"Booking: {booking.pk}\n"
        f"Listing: {booking.listing.title}\n"
        f"Check-in: {booking.start_date}\n"
        f"Check-out: {booking.end_date}\n"
        f"Guests: {booking.guests_count}\n"
        f"With pets: {'yes' if booking.has_pets else 'no'}\n"
        f"Total price: {booking.total_price}\n"
        f"Status: {booking.get_status_display()}\n"
    )

    if booking.decision_reason:
        body += (
            f"Decision reason: "
            f"{booking.get_decision_reason_display()}\n"
        )

    if booking.status == Status.PENDING and booking.review_deadline is not None:
        deadline = timezone.localtime(booking.review_deadline,)
        body += (f"Review deadline: {deadline:%d.%m.%Y %H:%M %Z}\n"
                    "Dates are not reserved during the review period.\n")
    if booking.description:
        body += f"Renter comment: {booking.description}\n"

    recipients = tuple(sorted({booking.user.email, booking.listing.user.email,}))

    callback = partial(send_booking_emails, booking_id=booking.pk, # partial() подготавливает вызов функции с конкретными данными письма.
                       subject=subject, body=body, recipients=recipients) # Данные фиксируются в момент события,
                                                                        # поэтому последующие изменения объекта не изменят уже подготовленное сообщение.
    transaction.on_commit(callback, using=using, robust=True)