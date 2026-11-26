"""Добавить мягкое удаление вложений и перенести состояние объявлений."""

from django.db import migrations, models


def mark_existing_files(apps, schema_editor):
    """Пометить вложения ранее мягко удалённых объявлений."""
    Listing = apps.get_model("listings", "Listing")
    ListingFile = apps.get_model("listings", "ListingFile")
    alias = schema_editor.connection.alias

    deleted_listings = (
        Listing.objects.using(alias)
        .filter(deleted_at__isnull=False)
        .values_list("pk", "deleted_at")
    )

    for listing_id, deleted_at in deleted_listings.iterator():
        ListingFile.objects.using(alias).filter(
            listing_id=listing_id,
        ).update(deleted_at=deleted_at)


class Migration(migrations.Migration):
    dependencies = [
        ("listings", "0006_alter_listing_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="listingfile",
            name="deleted_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.RunPython(
            mark_existing_files,
            migrations.RunPython.noop,
        ),
    ]