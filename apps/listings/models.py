from django.db import models
import re

from apps.listings.utils.validators import (
    validate_file_extension,
    validate_file_size,
    state_code_validator,
    property_file_upload_to,
    ags_validator,
    validate_plz,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.base.models import TimeStampModel, UUIDModel
from django.conf import settings

# Create your models here.
from .choices import Types


class Property(UUIDModel, TimeStampModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL
                             , on_delete=models.CASCADE
                             , related_name='properties')
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    price_per_night = models.DecimalField(max_digits=10
                                          , decimal_places=2
                                          , null=True, blank=True
                                          , verbose_name=_("Price per night"))
    rooms = models.DecimalField(max_digits=4, decimal_places=1
                                , null=True, blank=True
                                , verbose_name=_("Rooms"))
    is_active = models.BooleanField(default=True)
    property_type = models.CharField(max_length=15, choices=Types, verbose_name=_("Type"))

    # files = models.ManyToManyField(PropertyFile, related_name="properties", blank=True, verbose_name=_("Files"))

    class Meta:
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

    def __str__(self):
        return f"{self.title} ({self.pk})"


class PropertyFile(UUIDModel, TimeStampModel):
    """Файл с названием, путём хранения и датой создания; может принадлежать одному объявлению."""
    title = models.CharField(max_length=120, verbose_name=_("Title of the file"))
    file = models.FileField(upload_to=property_file_upload_to
                            , validators=[validate_file_size
            , validate_file_extension]
                            , verbose_name=_("File"))
    property = models.ForeignKey(Property, on_delete=models.CASCADE
                                 , related_name="files"
                                 , verbose_name=_("Property"))

    # created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        """Таблица, подписи, порядок и ограничения модели PropertyFile."""
        db_table = 'property_files'
        ordering = ['title', '-created_at']
        verbose_name = _('Property file')
        verbose_name_plural = _('Property files')

    def __str__(self):
        return f"{self.title}"


class State(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name=_("Federal state"))
    code = models.CharField(max_length=2
                            , primary_key=True
                            , validators=[state_code_validator]
                            , verbose_name=_("Federal state code"))

    class Meta:
        db_table = 'states'
        ordering = ['name']
        verbose_name = _('State')
        verbose_name_plural = _('States')

    def __str__(self):
        return f"{self.name} ({self.code})"


class City(models.Model):
    ags = models.CharField(max_length=8, unique=True
                           , validators=[ags_validator]
                           , verbose_name=_("Official municipality code"))
    name = models.CharField(max_length=150, verbose_name=_("City"))
    state = models.ForeignKey(State, on_delete=models.PROTECT
                              , related_name="cities"
                              , verbose_name=_("Federal state"))

    class Meta:
        db_table = 'cities'
        ordering = ['name']
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    def __str__(self):
        return f"{self.name} ({self.ags})"


class Address(models.Model):
    property = models.OneToOneField(Property
                                    , on_delete=models.CASCADE
                                    , related_name="address")
    # state = models.CharField(max_length=80, choices=States, verbose_name=_("State"))
    city = models.ForeignKey(City, on_delete=models.PROTECT
                             , related_name="addresses"
                             , verbose_name=_("City"))
    street = models.CharField(max_length=100, verbose_name=_("Street"))
    house = models.CharField(max_length=15, verbose_name=_("House"))
    plz = models.CharField(max_length=5, blank=True, validators=[validate_plz], verbose_name=_("Plz"))

    class Meta:
        db_table = 'addresses'
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
