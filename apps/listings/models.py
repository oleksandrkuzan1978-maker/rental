"""Объявления о недвижимости, вложения, адреса и справочники Германии."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.listings.utils.validators import (
    validate_file_extension,
    validate_file_size,
    state_code_validator,
    property_file_upload_to,
    ags_validator,
    validate_plz,
)
from django.db import transaction
from apps.base.models import TimeStampModel, UUIDModel
from django.conf import settings

# Create your models here.


class Types(models.TextChoices):
    """Допустимые типы объектов недвижимости."""

    APARTMENT = "apartment", _("Apartment")
    HOUSE = "house", _("House")
    STUDIO = "studio", _("Studio")
    ROOM = "room", _("Room")
    TOWNHOUSE = "townhouse", _("Townhouse")


class Property(UUIDModel, TimeStampModel):
    """Объявление владельца с типом жилья, тарифом и статусом активности."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL
                             , on_delete=models.CASCADE
                             , related_name='properties')
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    price_per_night = models.DecimalField(max_digits=10
                                          , decimal_places=2
                                          , verbose_name=_("Price per night"))
    rooms = models.DecimalField(max_digits=4, decimal_places=1
                                , null=True, blank=True
                                , verbose_name=_("Rooms"))
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    property_type = models.CharField(max_length=15, choices=Types, verbose_name=_("Type"))

    # files = models.ManyToManyField(PropertyFile, related_name="properties", blank=True, verbose_name=_("Files"))

    class Meta:
        """Порядок выдачи и допустимые значения цены, комнат и типа жилья."""

        db_table = 'properties'
        verbose_name = _('Property')
        verbose_name_plural = _('Properties')
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                        models.Q(price_per_night__isnull=True)
                        | models.Q(price_per_night__gt=0)
                ),
                name="property_price_positive_or_null",
            ),
            models.CheckConstraint(
                condition=(
                        models.Q(rooms__isnull=True)
                        | models.Q(rooms__gt=0)
                ),
                name="property_rooms_positive_or_null",
            ),
            models.CheckConstraint(condition=models.Q(property_type__in=Types.values),
                                   name='property_type_valid')]

    def soft_delete(self):
        with transaction.atomic():
            now = timezone.now()

            self.is_active = False
            self.deleted_at = now

            self.save(update_fields=[
                'is_active',
                'deleted_at'
            ])
            self.files.update(
                deleted_at=now
            )

    def __str__(self):
        """Вернуть заголовок объявления вместе с его идентификатором."""
        return f"{self.title} ({self.pk})"


class PropertyFile(UUIDModel, TimeStampModel):
    """Вложение объявления с названием и путём к файлу в хранилище."""

    title = models.CharField(max_length=120, verbose_name=_("Title of the file"))
    file = models.FileField(max_length=255, upload_to=property_file_upload_to
                            , validators=[validate_file_size
            , validate_file_extension]
                            , verbose_name=_("File"))
    property = models.ForeignKey(Property, on_delete=models.CASCADE
                                 , related_name="files"
                                 , verbose_name=_("Property"))
    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )
    # Подумать про еще пару полей:
    # is_main	BOOLEAN	Главное фото
    # sort_order	INT UNSIGNED	Порядок отображения
    # created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        """Настройки таблицы и порядка выдачи вложений."""

        db_table = 'property_files'
        ordering = ['title', '-created_at']
        verbose_name = _('Property file')
        verbose_name_plural = _('Property files')

    def __str__(self):
        """Вернуть название вложения."""
        return f"{self.title}"


class State(models.Model):
    """Федеральная земля Германии с двухзначным кодом."""

    name = models.CharField(max_length=80, unique=True, verbose_name=_("Federal state"))
    code = models.CharField(max_length=2
                            , primary_key=True
                            , validators=[state_code_validator]
                            , verbose_name=_("Federal state code"))

    class Meta:
        """Настройки таблицы и алфавитной сортировки земель."""

        db_table = 'states'
        ordering = ['name']
        verbose_name = _('State')
        verbose_name_plural = _('States')

    def __str__(self):
        """Вернуть название федеральной земли и её код."""
        return f"{self.name} ({self.code})"


class City(models.Model):
    """Муниципалитет Германии с кодом AGS и ссылкой на федеральную землю."""

    ags = models.CharField(max_length=8, unique=True
                           , validators=[ags_validator]
                           , verbose_name=_("Official municipality code"))
    name = models.CharField(max_length=150, verbose_name=_("City"))
    state = models.ForeignKey(State, on_delete=models.PROTECT
                              , related_name="cities"
                              , verbose_name=_("Federal state"))

    class Meta:
        """Настройки таблицы и алфавитной сортировки муниципалитетов."""

        db_table = 'cities'
        ordering = ['name']
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    def __str__(self):
        """Вернуть название муниципалитета и его код AGS."""
        return f"{self.name} ({self.ags})"


class CityDistrict(models.Model):
    """Именованная часть муниципалитета с идентификатором из источника."""

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="districts",
        verbose_name=_("City")
    )
    code = models.CharField(max_length=32, verbose_name=_("CityDistrict code"))
    name = models.CharField(max_length=150, verbose_name=_("CityDistrict name") )

    class Meta:
        """Настройки сортировки и уникальности кода района в пределах города."""

        db_table = 'city_districts'
        ordering = ["name", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "code"],
                name="city_district_unique_code",
            ),
        ]

    def __str__(self):
        """Вернуть название района."""
        return self.name


class Address(models.Model):
    """Адрес объявления с муниципалитетом, улицей, домом и индексом."""

    property = models.OneToOneField(Property
                                    , on_delete=models.CASCADE
                                    , related_name="address")
    # state = models.CharField(max_length=80, choices=States, verbose_name=_("State"))
    city = models.ForeignKey(City, on_delete=models.PROTECT
                             , related_name="addresses"
                             , verbose_name=_("City"))
    street = models.CharField(max_length=100, verbose_name=_("Street"))
    house = models.CharField(max_length=15, verbose_name=_("House"))
    plz = models.CharField(max_length=5, blank=True, validators=[validate_plz], verbose_name=_("PLZ"))

    class Meta:
        """Настройки таблицы адресов и названий для интерфейса."""

        db_table = 'addresses'
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
