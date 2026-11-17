from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

phone_validator = RegexValidator(
    regex=r"^\+[1-9]\d{1,14}$",
    message=_("Enter the phone number in international format E.164 (for example: +4915123456789)"),
)