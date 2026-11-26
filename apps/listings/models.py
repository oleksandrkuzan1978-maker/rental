"""Объявления о недвижимости, вложения, адреса и справочники Германии."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
# from django.utils import timezone
# from django.db import transaction
from apps.base.models import TimeStampModel, UUIDModel, SoftDeleteModel
from django.conf import settings

from apps.listings.utils.choices import Types, ListingStatus
from apps.listings.utils.validators import (
    validate_file_extension,
    validate_file_size,
    state_code_validator,
    listing_file_upload_to,
    ags_validator,
    validate_plz,
)
from .utils.variables import (
    DEFAULT_CHECK_IN_TIME,
    DEFAULT_CHECK_OUT_TIME,
    MIN_PRICE_PER_NIGHT,
    MAX_ROOMS,
)


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
        return f"{_("State")}: {self.name} ({self.code})"


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
        indexes = [models.Index(
    fields=['state', 'name'],
    name='city_state_name_idx',
)]

    def __str__(self):
        """Вернуть название муниципалитета и его код AGS."""
        return f"{_('City')}: {self.name} ({self.ags})"


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
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=["city", "code"],
        #         name="city_district_unique_code",
        #     ),
        # ]

    def __str__(self):
        """Вернуть название района и его города."""
        return f'{_('District name')}: {self.name}'


class Listing(UUIDModel, TimeStampModel, SoftDeleteModel):
    """Объявление владельца с типом жилья, тарифом и статусом активности."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL
                             , on_delete=models.PROTECT
                             , related_name='listings')
    title = models.CharField(max_length=254, verbose_name=_('Title'))
    description = models.TextField(blank=True, validators=[MaxLengthValidator(5000)], verbose_name=_("Description"))
    price_per_night = models.DecimalField(max_digits=10
                                          , decimal_places=2
                                          , blank=True, null=True
                                          , validators=[MinValueValidator(MIN_PRICE_PER_NIGHT)]
                                          , verbose_name=_("Price per night"))
    rooms = models.DecimalField(max_digits=4, decimal_places=1
                                , null=True, blank=True
                                , validators=[MaxValueValidator(MAX_ROOMS)]
                                , verbose_name=_("Rooms"))
    status = models.CharField(
        max_length=10,
        choices=ListingStatus,
        default=ListingStatus.DRAFT,
    )
    #is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    property_type = models.CharField(max_length=15, choices=Types, verbose_name=_("Type"))

    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, blank=True
                             , related_name="listings"
                             , verbose_name=_("City"))
    city_district = models.ForeignKey(
        CityDistrict,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="listings",
    )
    street = models.CharField(max_length=100, blank=True, verbose_name=_("Street"))
    house = models.CharField(max_length=15, blank=True, verbose_name=_("House"))
    apartment = models.CharField(max_length=15, blank=True, default="", verbose_name=_("Apartment"),)
    plz = models.CharField(max_length=5, blank=True, validators=[validate_plz], verbose_name=_("PLZ"))

    show_phone = models.BooleanField(default=True) # Флаги показа контактов в моделях
    show_email = models.BooleanField(default=True)

    max_guests = models.PositiveIntegerField(null=True, blank=True
                                             , validators=[MinValueValidator(1)]
                                             , verbose_name=_("Maximum number of guests"))
    pets_allowed = models.BooleanField(default=False, verbose_name=_("Pet allowed"))
    instant_booking_enabled = models.BooleanField(default=True
                                                  , verbose_name=_(
                                                    "Instant booking enabled")) # флаг мгновенного бронирования
    check_in_time = models.TimeField(
        default=DEFAULT_CHECK_IN_TIME,
        verbose_name=_("Check-in from"),
    )

    check_out_time = models.TimeField(
        default=DEFAULT_CHECK_OUT_TIME,
        verbose_name=_("Check-out by"),
    )

    class Meta:
        """Порядок выдачи и допустимые значения цены, комнат и типа жилья."""

        db_table = 'listings'
        verbose_name = _('Listing')
        verbose_name_plural = _('Listings')
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["city", "status", "property_type"],
                name="prop_city_status_type_idx",
            ),
            models.Index(
                fields=["city", "status", "price_per_night"],
                name="prop_city_status_price_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                        models.Q(price_per_night__isnull=True)
                        | models.Q(price_per_night__gte=MIN_PRICE_PER_NIGHT)
                ),
                name="property_min_price_or_null",
            ),
            models.CheckConstraint(
                condition=(
                        models.Q(rooms__isnull=True)
                        | models.Q(rooms__gt=0)
                ),
                name="property_rooms_positive_or_null",
            ),
            models.CheckConstraint(
                condition=(
                        models.Q(rooms__isnull=True)
                        | models.Q(rooms__lte=MAX_ROOMS)
                ),
                name="listing_rooms_max",
            ),
            models.CheckConstraint(condition=models.Q(property_type__in=Types.values)
                                     , name='property_type_valid')
            , models.CheckConstraint(condition=(models.Q(deleted_at__isnull=True)
                                                | ~models.Q(status=ListingStatus.PUBLISHED))
                                     , name="listing_deleted_at_", )
            , models.CheckConstraint(condition=models.Q(status__in=ListingStatus.values)
                                     , name='listing_status_in')
            , models.CheckConstraint(condition=models.Q(max_guests__isnull=True)
                                                | models.Q(max_guests__gte=1)
                                     , name="listing_max_guests_positive")
            , models.UniqueConstraint(fields=["city", "street", "house", "apartment", "plz"]
                                      , name="unique_address"
                                      , violation_error_message=_("An ad with this city, street, "
                                                                  "house number, and postal code already exists."))
]

    def clean(self):
        """Проверить, что выбранный район относится к указанному городу
        и проверить готовность объявления к публикации."""
        super().clean()
        errors = {}

        if self.city_district_id is not None:
            district_matches = CityDistrict.objects.filter(
                pk=self.city_district_id,
                city_id=self.city_id,
            ).exists()
            if not district_matches:
                errors["city_district"] = _( "Select the district that belongs to the specified city.")

        if self.status == ListingStatus.PUBLISHED:
            if self.city_id is None:
                errors["city"] = _("Specify the city before publishing the listing.")
            if not self.street.strip():
                errors["street"] = _("Specify the street before publishing the listing.")
            if not self.house.strip():
                errors["house"] = _("Specify the house before publishing the listing.")
            if self.price_per_night is None:
                errors["price_per_night"] = _("Specify the price before publishing the listing.")
            if self.max_guests is None:
                errors["max_guests"] = _("Specify the maximum number of guests before publishing.")

        if errors:
            raise ValidationError(errors)

    #
    # def soft_delete(self):
    #     """Деактивировать объявление и сохранить время его мягкого удаления."""
    #     # подумать: в будущем добавить менеджер, который будет
    #     # автоматически исключать мягко удалённые объявления из обычной выдачи.
    #     with transaction.atomic():
    #         if self.deleted_at is not None: # защита от повторного мягкого удаления
    #             return
    #
    #         self.status = ListingStatus.PAUSED
    #         self.deleted_at = timezone.now()
    #
    #         self.save(update_fields=[
    #             'status',
    #             'deleted_at',
    #             'updated_at'
    #         ])

    def __str__(self):
        """Вернуть заголовок объявления вместе с его идентификатором."""
        return f"Listing: '{self.title}', ({self.pk})"


class ListingFile(UUIDModel, TimeStampModel, SoftDeleteModel):
    """Вложение объявления с названием и путём к файлу в хранилище."""

    title = models.CharField(max_length=120, verbose_name=_("Title of the file"))
    file = models.FileField(max_length=255, upload_to=listing_file_upload_to
                            , validators=[validate_file_size
            , validate_file_extension]
                            , verbose_name=_("File"))
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE
                                , related_name="files"
                                , verbose_name=_("Listing"))
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Настройки таблицы и порядка выдачи вложений."""

        db_table = 'listing_files'
        ordering = ['title', '-created_at']
        verbose_name = _('Listing file')
        verbose_name_plural = _('Listing files')

    def __str__(self):
        """Вернуть название вложения."""
        return f"ListingFile: {self.title}"
