from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from openpyxl import load_workbook
from apps.listings.models import City, State


class Command(BaseCommand):
    help = "Import German municipalities from Destatis Excel file"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file'
            , required=True
            , help='Path to Excel file with municipalities')

    @staticmethod
    def normalize_code(value, length):
        """
        Converts a code into a string of the required length.
        Example: 1 -> '01', 5 -> '005'.
        """
        if value is None:
            raise ValueError("Code cannot be empty")

        try:
            number = int(value)
        except (ValueError, TypeError, OverflowError):
            raise ValueError(f"Invalid code: {value!r}")

        if number < 0 or number >= 10 ** length:
            raise ValueError(f"Code has invalid length: {value!r}")
        return str(number).zfill(length)

    def handle(self, *args, **options):
        file_path = Path(options["file"])

        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")
        try:
            workbook = load_workbook(file_path, read_only=True, data_only=True)
        except Exception as error:
            raise CommandError(f"Cannot open Excel file: {error}")

        try:
            sheet_name = "Onlineprodukt_Gemeinden30092026"
            if sheet_name not in workbook.sheetnames:
                raise CommandError(f"Sheet {sheet_name} not found")
            worksheet = workbook[sheet_name]

            states_imported = 0
            cities_imported = 0

            with transaction.atomic():
                for row in worksheet.iter_rows(min_row=7, values_only=True):
                    record_type = str(row[0]).strip() if row[0] is not None else ""
                    # ---------------------------------
                    # 1. Import federal states
                    # Satzart = 10
                    # ---------------------------------
                    if record_type == "10":
                        state_code = self.normalize_code(row[2], 2)

                        if row[7] is None:
                            raise CommandError(f"Missing state name for code {state_code}")

                        state_name = str(row[7]).strip()

                        if not state_name:
                            raise CommandError(f"Empty state name for code {state_code}")

                        State.objects.update_or_create(code=state_code, defaults={"name": state_name},)
                        states_imported += 1
                    # ---------------------------------
                    # 2. Import municipalities
                    # Satzart = 60
                    # ---------------------------------
                    elif record_type == "60":

                        land = self.normalize_code(row[2], 2)
                        rb = self.normalize_code(row[3], 1)
                        kreis = self.normalize_code(row[4], 2)
                        gemeinde = self.normalize_code(row[6], 3)

                        # AGS consists of:
                        # Land + RB + Kreis + Gem
                        ags = land + rb + kreis + gemeinde

                        if row[7] is None:
                            raise CommandError(f"Missing city name for code {ags}")

                        city_name = str(row[7]).strip()

                        if not city_name:
                            raise CommandError(f"Empty city name for code {ags}")


                        try:
                            state = State.objects.get(code=land)
                        except State.DoesNotExist:
                            raise CommandError(
                                f"State {land} not found for {city_name}"
                            )

                        City.objects.update_or_create(
                            ags=ags,
                            defaults={
                                "name": city_name,
                                "state": state,
                            },
                        )

                        cities_imported += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Import completed successfully!\n"
                    f"Federal states processed: {states_imported}\n"
                    f"Municipalities processed: {cities_imported}"
                )
            )

        finally:
            workbook.close()