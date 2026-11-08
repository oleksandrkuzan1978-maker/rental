from django.db import models
from django.utils.translation import gettext_lazy as _


class Types(models.TextChoices):
    APARTMENT = "apartment", _("Apartment")
    HOUSE = "house", _("House")
    STUDIO = "studio", _("Studio")
    ROOM = "room", _("Room")
    TOWNHOUSE = "townhouse", _("Townhouse")


# class States(models.TextChoices):
#     BW = "BW", _("Baden-Württemberg")
#     BY = "BY", _("Bayern")
#     BE = "BE", _("Berlin")
#     BB = "BB", _("Brandenburg")
#     HB = "HB", _("Bremen")
#     HH = "HH", _("Hamburg")
#     HE = "HE", _("Hessen")
#     MV = "MV", _("Mecklenburg-Vorpommern")
#     NI = "NI", _("Niedersachsen")
#     NW = "NW", _("Nordrhein-Westfalen")
#     RP = "RP", _("Rheinland-Pfalz")
#     SL = "SL", _("Saarland")
#     SN = "SN", _("Sachsen")
#     ST = "ST", _("Sachsen-Anhalt")
#     SH = "SH", _("Schleswig-Holstein")
#     TH = "TH", _("Thüringen")