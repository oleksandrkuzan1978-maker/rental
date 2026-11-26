"""Очистка хранилища после физического удаления вложений."""

from functools import partial

from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ListingFile


@receiver(
    post_delete,
    sender=ListingFile,
    dispatch_uid="listings.delete_attachment_file",
)
def delete_attachment_file(sender, instance, using, **kwargs):
    """Удалить файл физически после успешной фиксации удаления записи."""
    if instance.file.name:
        # on_commit() принципиален: если удаление записей откатится, файл останется на месте
        transaction.on_commit(
            partial(
                instance.file.storage.delete,
                instance.file.name,
            ),
            using=using,
            robust=True,
        )