"""Валидаторы адресных кодов и вложений, а также построение пути загрузки."""

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from pathlib import Path
import re
# Допустимые расширения файлов

ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "pdf"]

validate_file_extension = FileExtensionValidator(
    allowed_extensions=ALLOWED_EXTENSIONS,
)

state_code_validator = RegexValidator(
        regex=r"^[0-9]{2}$",
        message=_("Federal state code must contain exactly 2 digits."),
    )

ags_validator = RegexValidator(
    regex=r"^[0-9]{8}$",
    message=_("AGS must contain exactly 8 digits."),
)

# Максимальный размер файла — 2 МиБ
def validate_file_size(file):
    """Вызвать ValidationError для файла размером больше 2 МиБ."""
    max_size = 2 * 1024 * 1024

    if file.size > max_size:
        raise ValidationError(
            _("File size must not exceed 2 MB.")
        )


def validate_plz(value):
    """Проверить, что почтовый индекс состоит ровно из пяти цифр."""
    if not re.fullmatch(r"[0-9]{5}", value):
        raise ValidationError(
            "PLZ muss aus genau 5 Ziffern bestehen."
        )


def property_file_upload_to(instance, filename):
    """Вернуть путь к файлу по UUID владельца, объявления и вложения.

    Расширение берётся из filename и переводится в нижний регистр.
    """
    extension = Path(filename).suffix.lower()
    return (
        f"users/{instance.property.user_id}/"
        f"properties/{instance.property_id}/"
        f"{instance.pk}{extension}"
    )