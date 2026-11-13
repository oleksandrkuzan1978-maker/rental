"""Импорт районов из общегерманского архива BKG GN250.

Используйте команду python manage.py import_districts --file ПУТЬ_К_ZIP.
"""

import csv
from io import TextIOWrapper
from pathlib import PurePosixPath
from zipfile import BadZipFile, ZipFile

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.listings.models import City, CityDistrict


class Command(BaseCommand):
    """Команда Django для загрузки районов в существующий справочник городов."""

    help = "Import districts from the BKG GN250 CSV archive."

    def add_arguments(self, parser):
        """Добавить обязательный параметр --file с путём к архиву GN250."""
        parser.add_argument("--file", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        """Прочитать GN250.CSV из архива и импортировать районы в транзакции.

        Вывести число обработанных записей и сообщить о строках без города.
        """
        cities = dict(City.objects.values_list("ags", "pk"))
        if not cities:
            raise CommandError("Import cities first with import_cities.")

        try:
            with ZipFile(options["file"]) as archive:
                member = next(
                    (
                        name
                        for name in archive.namelist()
                        if PurePosixPath(name).name.casefold() == "gn250.csv"
                    ),
                    None,
                )
                if member is None:
                    raise CommandError("The archive does not contain GN250.CSV.")

                with archive.open(member) as raw:
                    with TextIOWrapper(raw, encoding="utf-8-sig", newline="") as source:
                        created, found, unmatched = self.import_rows(source, cities)
        except (OSError, BadZipFile, UnicodeError, csv.Error) as error:
            raise CommandError(f"Cannot read the GN250 archive: {error}") from error

        if unmatched:
            examples = ", ".join(sorted(set(unmatched))[:5])
            self.stderr.write(
                f"Skipped {len(unmatched)} rows with no matching city. "
                f"Examples: {examples}."
            )

        if not created and not found:
            raise CommandError("No districts matched the city directory.")

        self.stdout.write(self.style.SUCCESS(
            f"Created: {created}. Existing rows processed: {found}."
        ))

    def import_rows(self, source, cities):
        """Добавить или обновить районы из открытого CSV.

        Параметр cities сопоставляет AGS с первичными ключами городов.
        Вернуть число новых строк, число обработанных существующих строк
        и список кодов, для которых город не найден.
        """
        rows = csv.DictReader(source, delimiter=";", strict=True)
        required = {"AGS", "NNID", "NAME", "GEMTEIL", "VIRTUELL"}
        if not required.issubset(rows.fieldnames or ()):
            raise CommandError("GN250.CSV is missing required columns.")

        yes = {"ja", "j", "1", "true"}
        created = found = 0
        unmatched = []

        for row in rows:
            if (row["GEMTEIL"] or "").strip().casefold() not in yes:
                continue
            if (row["VIRTUELL"] or "").strip().casefold() in yes:
                continue

            ags = (row["AGS"] or "").strip()
            ars = (row.get("ARS") or "").strip()
            if not ags and len(ars) == 12 and ars.isascii() and ars.isdigit():
                ags = ars[:5] + ars[9:]

            city_id = cities.get(ags)
            if city_id is None:
                unmatched.append(ags or "<empty>")
                continue

            code = (row["NNID"] or "").strip()
            name = (row["NAME"] or "").strip()
            if not code or len(code) > 32 or not name or len(name) > 150:
                raise CommandError(f"Line {rows.line_num}: invalid NNID or NAME.")

            _, was_created = CityDistrict.objects.update_or_create(
                city_id=city_id,
                code=code,
                defaults={"name": name},
            )
            if was_created:
                created += 1
            else:
                found += 1

        return created, found, unmatched


#Запустить импорт
# Из корня проекта выполните:
#.\.venv\Scripts\python.exe manage.py makemigrations
# .\.venv\Scripts\python.exe manage.py migrate
# .\.venv\Scripts\python.exe manage.py import_cities --file "data\germany\AuszugGV3QAktuell - Copy.xlsx"
# .\.venv\Scripts\python.exe manage.py import_districts --file "data\germany\gn250.utm32s.csv.zip"
