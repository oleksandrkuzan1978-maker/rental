from django.db import models
from django.utils.translation import gettext_lazy as _


class Status(models.TextChoices):
    """Допустимые статусы бронирования."""

    PENDING = "pending", _("Pending")
    CONFIRMED = "confirmed", _("Confirmed")
    REJECTED = "rejected", _("Rejected")
    CANCELLED = "cancelled", _("Cancelled") # отменено
    COMPLETED = "completed", _("Completed") # завершено


class DecisionReason(models.TextChoices):
    """Причины подтверждения и отклонения заявки."""

    AUTO_CONFIRMED = "auto_confirmed", _("Automatically confirmed")
    OWNER_CONFIRMED = "owner_confirmed", _("Confirmed by the owner")

    CAPACITY_EXCEEDED = "capacity_exceeded", _("Guest capacity exceeded")
    PETS_NOT_ALLOWED = "pets_not_allowed", _("Pets are not allowed")
    DATES_UNAVAILABLE = "dates_unavailable", _("Dates are no longer available")
    LISTING_UNAVAILABLE = "listing_unavailable", _("Listing is unavailable")
    OWNER_REJECTED = "owner_rejected", _("Rejected by the owner")
    REVIEW_TIMEOUT = "review_timeout", _("Owner response deadline expired")

    USER_CANCELLED = "user_cancelled", _("Cancelled by the tenant")

    ACCOUNT_DELETED = "account_deleted", _("Cancelled because an account was deleted")