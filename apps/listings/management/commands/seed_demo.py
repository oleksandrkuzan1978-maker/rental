"""Заполнение таблиц проекта демонстрационными данными.

Запустите python manage.py seed_demo после миграций и импорта городов.
"""

from base64 import b64decode
from datetime import timedelta
from decimal import Decimal
from secrets import token_urlsafe

from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.analytics.models import PropertyView, SearchHistory
from apps.bookings.models import Booking
from apps.bookings.services import confirm_booking, create_booking
from apps.listings.models import Address, City, Property, PropertyFile, Types
from apps.reviews.services import create_review
from apps.users.models import User


LANDLORD_EMAIL = "demo.landlord@example.invalid"
TENANT_EMAIL = "demo.tenant@example.invalid"
DEMO_PNG = b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAGAAAABACAIAAABqVuVZAAABZUlEQVR4nO3YP04CYRCG8dkNDZ134BAeQHoqr2LhASy4CpWVMQ4H4AjEmFjbWNoZLwD7+uebmQ98nhJIlv0xs8AOz2+fRscbJ54jgHRMkAggEUAigEQAiQASASQCSASQCCARQCKATg3Ib6+sp8YOdbwno6GTG2Z+CGV5t7XqupggPzIyPYxSPZBPKpQbFa+Yf/v8q9atDMh/PholRjUr5r9anJJ1K5gg//N5Zo5S9gR5iynIHKW8CfLWZ5UzR0lAHvaZRzNlrJhHbkT0usVOkGddLOLmKBDI07+VI5iiVswrfrNEHDQEyOv+QDU/dOMV8+r/ls3XbTxLHWv3ZgIv0ov5znJ7+bg8w/tBnQeQCCARQCKARACJZtZH1zf3Bx/frFdWGhMkAkgEkAggEUAigESz1/dHi2kxv7DcIs6FCRIBJAJIBJAIINHwtH9Qr/nXMUEigEQAiQASASQCSASQCCARQDbdF2KpY2w7jO9HAAAAAElFTkSuQmCC"
)


class Command(BaseCommand):
    """Команда Django для создания демонстрационных записей и вложений."""

    help = "Create demo users, listings, bookings, a review, and analytics events."
    requires_migrations_checks = True

    def handle(self, *args, **options):
        """Создать демонстрационные данные и очистить новые файлы при ошибке."""
        saved_files = []
        try:
            with transaction.atomic(durable=True):
                self.seed(saved_files)
        except Exception:
            # File storage does not participate in database transactions.
            for storage, name in saved_files:
                try:
                    storage.delete(name)
                except OSError as error:
                    self.stderr.write(f"Cannot remove demo file {name}: {error}")
            raise

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))

    def seed(self, saved_files):
        """Создать тестовые аккаунты, объявления, бронирования и события.

        В saved_files добавить пары из хранилища и пути, чтобы вызывающий
        метод мог удалить созданные файлы при откате.
        """
        if User.objects.filter(email__in=(LANDLORD_EMAIL, TENANT_EMAIL)).exists():
            raise CommandError("Demo accounts already exist. No new data was created.")

        cities = City.objects.in_bulk(("11000000", "05913000"), field_name="ags")
        if len(cities) != 2:
            raise CommandError("Import the cities first. Berlin and Dortmund are required.")

        landlord_group, _ = Group.objects.get_or_create(name="Landlord")
        tenant_group, _ = Group.objects.get_or_create(name="Tenant")
        Group.objects.get_or_create(name="Staff")

        # Use random passwords. Set a known password with manage.py changepassword.
        landlord = User.objects.create_user(
            email=LANDLORD_EMAIL, first_name="Demo landlord", password=token_urlsafe(24)
        )
        landlord.groups.add(landlord_group)
        tenant = User.objects.create_user(
            email=TENANT_EMAIL, first_name="Demo tenant", password=token_urlsafe(24)
        )
        tenant.groups.add(tenant_group)

        berlin = Property.objects.create(
            user=landlord,
            title="Demo: Apartment in Berlin",
            description="Fictional listing for testing the rental project.",
            property_type=Types.APARTMENT,
            price_per_night=Decimal("79.90"),
            rooms=2,
        )
        dortmund = Property.objects.create(
            user=landlord,
            title="Demo: Studio in Dortmund",
            description="Fictional listing for testing the rental project.",
            property_type=Types.STUDIO,
            price_per_night=Decimal("59.00"),
            rooms=1,
        )
        Address.objects.create(
            property=berlin, city=cities["11000000"], street="Demo-Straße", house="12a", plz="10115"
        )
        Address.objects.create(
            property=dortmund, city=cities["05913000"], street="Demo-Weg", house="5", plz="44135"
        )

        today = timezone.localdate()
        past = create_booking(
            user=tenant,
            property_id=berlin.pk,
            start_date=today - timedelta(days=14),
            end_date=today - timedelta(days=10),
        )
        past = confirm_booking(property_id=berlin.pk, booking_id=past.pk)
        past.status = Booking.Status.COMPLETED
        past.save(update_fields=["status", "updated_at"])
        create_review(user=tenant, booking_id=past.pk, rating=5, comment="Demo review.")

        upcoming = create_booking(
            user=tenant,
            property_id=berlin.pk,
            start_date=today + timedelta(days=7),
            end_date=today + timedelta(days=10),
        )
        confirm_booking(property_id=berlin.pk, booking_id=upcoming.pk)
        create_booking(
            user=tenant,
            property_id=dortmund.pk,
            start_date=today + timedelta(days=14),
            end_date=today + timedelta(days=16),
        )

        PropertyView.objects.create(property=berlin, user=tenant)
        PropertyView.objects.create(property=berlin)
        PropertyView.objects.create(property=dortmund, user=tenant)
        SearchHistory.objects.create(user=tenant, query="Wohnung Berlin")
        SearchHistory.objects.create(query="Wohnung Berlin")
        SearchHistory.objects.create(user=tenant, query="Studio Dortmund")

        for listing in (berlin, dortmund):
            attachment = PropertyFile(property=listing, title="Demo image")
            attachment.file.save("demo.png", ContentFile(DEMO_PNG), save=False)
            saved_files.append((attachment.file.storage, attachment.file.name))
            attachment.full_clean()
            attachment.save()
