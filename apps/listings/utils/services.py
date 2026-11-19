"""Операции с вложениями объявлений."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from apps.listings.models import Property, PropertyFile


MAX_FILES_PER_PROPERTY = 7


@transaction.atomic
def save_property_file(*, attachment):
    """Проверить лимит, сохранить вложение и вернуть его."""
    # Все загрузки к одному объявлению проходят проверку по очереди.
    listing = Property.objects.select_for_update().get(
        pk=attachment.property_id,
    )

    # При редактировании сам файл не занимает дополнительное место.
    other_files = listing.files.exclude(pk=attachment.pk)

    if other_files.count() >= MAX_FILES_PER_PROPERTY:
        raise ValidationError(
            _("You can attach a maximum of 7 files to a single listing."),
            code="property_file_limit",
        )

    attachment.full_clean()
    attachment.save()
    return attachment


def add_property_file(*, property_id, title, uploaded_file):
    """Создать вложение объявления с проверкой общего лимита файлов."""
    attachment = PropertyFile(
        property_id=property_id,
        title=title,
        file=uploaded_file,
    )
    return save_property_file(attachment=attachment)