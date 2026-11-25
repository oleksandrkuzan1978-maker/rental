from django.utils import timezone

def delete(self, using=None, keep_parents=False):
    """Мягкое удаление одного объекта."""
    if self.is_deleted:
        return 0, {"number of soft-deleted records": 0}

    self.is_deleted = True
    self.deleted_at = timezone.now()
    self.save(using=using
              , update_fields=["is_deleted", "deleted_at"]
              )
    return 1, {"number of soft-deleted records": 1}


def restore(self, using=None):
    """Восстановление одного объекта."""
    self.is_deleted = False
    self.deleted_at = None
    self.save(using=using, update_fields=["is_deleted", "deleted_at"])


def full_delete(self, using=None, keep_parents=False):
    """Физическое удаление одного объекта."""
    return super().delete(using=using, keep_parents=keep_parents, )
