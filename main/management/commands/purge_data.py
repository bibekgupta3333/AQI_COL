from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from main.models import WeatherData, Dataset, Dataset1, Dataset2, Dataset3
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Purge data from WeatherData and Dataset tables"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Skip confirmation prompts",
        )
        parser.add_argument(
            "--weather-only",
            action="store_true",
            help="Only purge WeatherData table",
        )
        parser.add_argument(
            "--dataset-only",
            action="store_true",
            help="Only purge Dataset tables",
        )

    def handle(self, *args, **options):
        try:
            purge_weather = not options["dataset_only"]
            purge_datasets = not options["weather_only"]

            if not purge_weather and not purge_datasets:
                raise CommandError("Must purge at least one type of data")

            if not options["force"]:
                if purge_weather:
                    weather_count = WeatherData.objects.count()
                    self.stdout.write(
                        self.style.WARNING(
                            f"This will delete {weather_count} records from WeatherData table"
                        )
                    )

                if purge_datasets:
                    dataset_count = Dataset.objects.count()
                    dataset1_count = Dataset1.objects.count()
                    dataset2_count = Dataset2.objects.count()
                    dataset3_count = Dataset3.objects.count()
                    self.stdout.write(
                        self.style.WARNING(
                            f"This will delete:"
                            f"\n - {dataset_count} records from Dataset table"
                            f"\n - {dataset1_count} records from Dataset1 table"
                            f"\n - {dataset2_count} records from Dataset2 table"
                            f"\n - {dataset3_count} records from Dataset3 table"
                        )
                    )

                confirm = input("\nAre you sure you want to continue? [y/N] ")
                if confirm.lower() != "y":
                    self.stdout.write(self.style.SUCCESS("Operation cancelled"))
                    return

            with transaction.atomic():
                if purge_weather:
                    weather_deleted = WeatherData.objects.all().delete()[0]
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Deleted {weather_deleted} records from WeatherData table"
                        )
                    )

                if purge_datasets:
                    dataset_deleted = Dataset.objects.all().delete()[0]
                    dataset1_deleted = Dataset1.objects.all().delete()[0]
                    dataset2_deleted = Dataset2.objects.all().delete()[0]
                    dataset3_deleted = Dataset3.objects.all().delete()[0]
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Deleted:"
                            f"\n - {dataset_deleted} records from Dataset table"
                            f"\n - {dataset1_deleted} records from Dataset1 table"
                            f"\n - {dataset2_deleted} records from Dataset2 table"
                            f"\n - {dataset3_deleted} records from Dataset3 table"
                        )
                    )

            self.stdout.write(self.style.SUCCESS("Data purge completed successfully"))

        except Exception as e:
            logger.error(f"Error in purge_data command: {str(e)}")
            raise CommandError(f"Command failed: {str(e)}")
