from django.db import models
from django.utils.translation import gettext_lazy as _

class Types(models.TextChoices):
    """Допустимые типы объектов недвижимости."""

    APARTMENT = "apartment", _("Apartment")
    HOUSE = "house", _("House")
    STUDIO = "studio", _("Studio")
    ROOM = "room", _("Room")
    TOWNHOUSE = "townhouse", _("Townhouse")


class ListingStatus(models.TextChoices):
    """Допустимые статусы объявления: черновик, опубликовано и приостановлено."""

    DRAFT = "draft", _("Draft") # режим черновика
    PUBLISHED = "published", _("Published") # Объявление активно
    PAUSED = "paused", _("Paused") # Объявление НЕ активно (is_active=False)