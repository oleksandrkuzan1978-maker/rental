"""Операции с вложениями объявлений."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from .models import Property, PropertyFile


MAX_FILES_PER_PROPERTY = 7


@transaction.atomic
def add_property_file(*, property_id, title, uploaded_file):
    """Добавить файл к объявлению и вернуть созданное вложение.

    Передайте идентификатор объявления property_id, название title и
    загруженный файл uploaded_file по имени. Запись создаётся в транзакции.
    Лимит в семь файлов и недопустимые данные вызывают ValidationError.
    Отсутствующее объявление вызывает Property.DoesNotExist.
    """
    listing = Property.objects.select_for_update().get(pk=property_id)

    if listing.files.count() >= MAX_FILES_PER_PROPERTY:
        raise ValidationError(
            _("You can attach a maximum of 7 files to a single listing."),
            code="property_file_limit",
        )

    attachment = PropertyFile(
        property=listing,
        title=title,
        file=uploaded_file,
    )
    attachment.full_clean()
    attachment.save()
    return attachment