from django.db import models
import uuid
from django.utils import timezone

# Create your models here.
class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Это поле хранит дату последнего изменения записи пользователя.

    class Meta:
        abstract = True