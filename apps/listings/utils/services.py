"""Операции с вложениями объявлений."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from apps.listings.models import Listing, ListingFile
from pathlib import Path

MAX_FILES_PER_LISTING = 7


@transaction.atomic
def save_listing_file(*, attachment):
    """Проверить лимит, сохранить вложение и вернуть его."""
    # Все загрузки к одному объявлению проходят проверку по очереди.
    listing = Listing.objects.select_for_update().get(
        pk=attachment.listing_id,
    )

    # При редактировании сам файл не занимает дополнительное место.
    other_files = listing.files.exclude(pk=attachment.pk)

    if other_files.count() >= MAX_FILES_PER_LISTING:
        raise ValidationError(
            _("You can attach a maximum of 7 files to a single listing."),
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


