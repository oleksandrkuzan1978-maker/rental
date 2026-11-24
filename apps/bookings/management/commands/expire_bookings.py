"""Автоматическое отклонение просроченных заявок."""
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.services import expire_booking
from apps.bookings.utils.choices import Status
from apps.bookings.utils.variables import MAINTENANCE_BATCH_SIZE

# Для автоматического запуска команды надо в Планировщике заданий Windows создать задачу.
# Для ручного запуска можно командную строку: python manage.py expire_bookings

class Command(BaseCommand):
    """Обработать порцию заявок с истёкшим сроком рассмотрения."""
    def handle(self, *args, **options):
        """Выбрать просроченные заявки и обработать каждую отдельно."""

        booking_ids = list(
            Booking.objects.filter(
                status=Status.PENDING,
                review_deadline__lte=timezone.now(),
            )
            .order_by("review_deadline", "pk")
            .values_list(
                "pk",
                flat=True,
            )[:MAINTENANCE_BATCH_SIZE]
        )
        errors = 0
        for booking_id in booking_ids:
            try:
                expire_booking(booking_id=booking_id)
            except Booking.DoesNotExist:
                # Запись могла исчезнуть после получения списка.
                continue

            except DatabaseError as error:
                errors += 1
                self.stderr.write(f"Failed to process booking {booking_id}: {error}")

        if errors:
            raise CommandError(f"Unprocessed requests: {errors}. "
                                "The next run will retry.")
        self.stdout.write(self.style.SUCCESS("Successfully expired bookings."))
