"""Операции с вложениями объявлений."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from apps.listings.models import Listing, ListingFile
from .variables import MAX_FILES_PER_LISTING


@transaction.atomic
def save_listing_file(*, attachment):
    """Сохранить неудалённое вложение с проверкой состояния и лимита."""
    listing = Listing.objects.select_for_update().get(
        pk=attachment.listing_id,
    )

    if listing.deleted_at is not None:
        raise ValidationError(
            _("Files cannot be saved for a deleted listing.")
        )

    if attachment.deleted_at is not None:
        raise ValidationError(
            _("A deleted file cannot be modified.")
        )

    if not attachment._state.adding:
        current = ListingFile.objects.select_for_update().get(
            pk=attachment.pk,
            listing_id=listing.pk,
        )

        if current.deleted_at is not None:
            raise ValidationError(
                _("A deleted file cannot be modified.")
            )

    other_files = listing.files.active().exclude(
        pk=attachment.pk,
    )

    if other_files.count() >= MAX_FILES_PER_LISTING:
        raise ValidationError(
            _(f"You can attach a maximum of {MAX_FILES_PER_LISTING} files to a single listing."),
            code="listing_file_limit",
        )

    attachment.full_clean()
    attachment.save()

    return attachment


def add_listing_file(*, listing_id, title, uploaded_file):
    """Создать вложение объявления с проверкой общего лимита файлов."""
    attachment = ListingFile(
        listing_id=listing_id,
        title=title,
        file=uploaded_file,
    )
    return save_listing_file(attachment=attachment)


