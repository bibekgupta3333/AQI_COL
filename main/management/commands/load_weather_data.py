"""
Django management command to load weather data from CSV files
Usage: python manage.py load_weather_data
"""

import csv
import logging
from datetime import datetime, time
from pathlib import Path
from typing import Dict, Optional
import decimal
import os
from django.utils import timezone
from zoneinfo import ZoneInfo

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction

from main.models import WeatherData

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load weather data from CSV files"

    def add_arguments(self, parser):
        parser.add_argument(
            "data_dir",
            type=str,
            help="Directory containing weather data CSV files",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without actually loading data",
        )
        parser.add_argument("--year", type=int, help="Filter data by year")

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])
        if not data_dir.exists():
            raise CommandError(f"Directory not found: {data_dir}")

        try:
            # Process all CSV files in the directory
            csv_files = list(data_dir.glob("*.csv"))
            if not csv_files:
                raise CommandError(f"No CSV files found in {data_dir}")

            total_processed = 0
            total_created = 0
            total_errors = 0

            for file_path in csv_files:
                if options["year"] and str(options["year"]) not in file_path.name:
                    continue

                if options["dry_run"]:
                    self.stdout.write(
                        self.style.WARNING(f"Dry run - would process: {file_path.name}")
                    )
                    processed, created, errors = self.load_csv_file(file_path, options)
                    total_processed += processed
                    total_created += created
                    total_errors += errors
                    continue

                processed, created, errors = self.load_csv_file(file_path, options)
                total_processed += processed
                total_created += created
                total_errors += errors

            if options["dry_run"]:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Dry run completed - no data was actually loaded."
                    )
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Completed: {total_processed} records processed, "
                    f"{total_created} new records created, "
                    f"{total_errors} errors"
                )
            )

        except Exception as e:
            logger.error(f"Error in load_weather_data command: {str(e)}")
            raise CommandError(f"Command failed: {str(e)}")

    def load_csv_file(self, file_path: Path, options: Dict):
        """Load data from a single CSV file"""
        self.stdout.write(f"\nProcessing: {file_path.name}")

        try:
            records_processed = 0
            records_created = 0
            errors = []

            with open(file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                # Show headers
                self.stdout.write(f"CSV headers: {list(reader.fieldnames)}")

                if options["dry_run"]:
                    # Just show first few rows
                    for i, row in enumerate(reader):
                        if i >= 5:  # Show first 5 rows
                            break
                        self.stdout.write(f"Row {i+1}: {dict(row)}")
                    return

                # Process all rows
                with transaction.atomic():
                    for row_num, row in enumerate(reader, start=2):
                        try:
                            processed_row = self.process_csv_row(row)
                            if processed_row:
                                # Create or update record using both date and hour
                                weather_record, created = (
                                    WeatherData.objects.update_or_create(
                                        date=processed_row["date"],
                                        timestamp=processed_row["timestamp"],
                                        location="Kathmandu",
                                        defaults={
                                            "temp_avg": processed_row.get("temp_avg"),
                                            "temp_max": processed_row.get("temp_max"),
                                            "temp_min": processed_row.get("temp_min"),
                                            "sea_level_pressure": processed_row.get(
                                                "sea_level_pressure"
                                            ),
                                            "humidity": processed_row.get("humidity"),
                                            "visibility": processed_row.get(
                                                "visibility"
                                            ),
                                            "wind_speed": processed_row.get(
                                                "wind_speed"
                                            ),
                                            "wind_gust": processed_row.get("wind_gust"),
                                            "aqi": processed_row.get("aqi"),
                                        },
                                    )
                                )

                                if created:
                                    records_created += 1
                                records_processed += 1

                        except Exception as e:
                            errors.append(f"Error in row {row_num}: {str(e)}")
                            logger.error(
                                f"Error processing row {row_num} in {file_path}: {str(e)}"
                            )

            if errors:
                self.stdout.write(
                    self.style.WARNING(f"Completed with {len(errors)} errors:")
                )
                for error in errors[:5]:  # Show first 5 errors
                    self.stdout.write(self.style.WARNING(f"  {error}"))
                if len(errors) > 5:
                    self.stdout.write(
                        self.style.WARNING(f"  ... and {len(errors) - 5} more errors")
                    )

            return records_processed, records_created, len(errors)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise CommandError(f"Failed to process {file_path}: {str(e)}")

    def process_csv_row(self, row: Dict) -> Optional[Dict]:
        """Process a single CSV row and return parsed data"""
        try:
            # Get date
            date_str = row.get("Date", "").strip()
            if not date_str:
                return None

            # Parse date - handle different formats including ISO format with timestamp
            date_obj = None
            timestamp_obj = None
            date_formats = [
                ("%Y-%m-%dT%H:%M:%S", True),  # ISO format with time
                ("%Y-%m-%d %H:%M:%S", True),  # ISO format with space
                ("%Y-%m-%d", False),  # Just date
                ("%d/%m/%Y", False),  # Other formats
                ("%m/%d/%Y", False),
                ("%d-%m-%Y", False),
                ("%m-%d-%Y", False),
            ]

            for fmt, has_time in date_formats:
                try:
                    if has_time:
                        timestamp_obj = datetime.strptime(date_str, fmt)
                        date_obj = timestamp_obj.date()
                        break
                    else:
                        date_obj = datetime.strptime(date_str, fmt).date()
                        # For dates without time, use the hour from the filename if available
                        hour = 12  # Default to noon
                        timestamp_obj = datetime.combine(date_obj, time(hour, 0))
                        break
                except ValueError:
                    continue

            if not date_obj or not timestamp_obj:
                raise ValueError(f"Could not parse date: {date_str}")

            # Make timestamp timezone-aware
            timestamp_obj = timestamp_obj.replace(tzinfo=ZoneInfo("Asia/Kathmandu"))

            def safe_float(
                value: str, decimal_places: int = 2, max_digits: int = 5
            ) -> Optional[float]:
                """Safely convert value to float with specified decimal places and max digits"""
                if not value or str(value).strip() in [
                    "---",
                    "NoData",
                    "nan",
                    "inf",
                    "-inf",
                ]:
                    return None
                try:
                    # Convert to float and round to specified decimal places
                    float_val = float(str(value).strip())

                    # Handle infinity and NaN
                    if (
                        float_val in [float("inf"), float("-inf")]
                        or float_val != float_val
                    ):  # != check for NaN
                        return None

                    # Round to specified decimal places
                    rounded_val = round(float_val, decimal_places)

                    # Check if the number exceeds max_digits
                    str_val = str(abs(rounded_val))
                    digits_before_decimal = len(str_val.split(".")[0])
                    if digits_before_decimal > (max_digits - decimal_places):
                        return None

                    return rounded_val
                except (ValueError, TypeError, decimal.InvalidOperation):
                    return None

            # Parse AQI as integer
            def safe_int(value: str) -> Optional[int]:
                """Safely convert value to integer"""
                if not value or str(value).strip() in ["---", "NoData"]:
                    return None
                try:
                    return int(
                        float(str(value).strip())
                    )  # Handle both int and float strings
                except (ValueError, TypeError):
                    return None

            return {
                "date": date_obj,
                "timestamp": timestamp_obj,
                "temp_avg": safe_float(
                    row.get("T"), 2, 5
                ),  # max_digits=5, decimal_places=2
                "temp_max": safe_float(
                    row.get("TM"), 2, 5
                ),  # max_digits=5, decimal_places=2
                "temp_min": safe_float(
                    row.get("Tm"), 2, 5
                ),  # max_digits=5, decimal_places=2
                "sea_level_pressure": safe_float(
                    row.get("SLP"), 2, 7
                ),  # max_digits=7, decimal_places=2
                "humidity": safe_float(
                    row.get("H"), 2, 5
                ),  # max_digits=5, decimal_places=2
                "visibility": safe_float(
                    row.get("VV"), 2, 5
                ),  # max_digits=5, decimal_places=2
                "wind_speed": safe_float(
                    row.get("V"), 2, 5
                ),  # max_digits=5, decimal_places=2
                "wind_gust": safe_float(
                    row.get("VM"), 2, 5
                ),  # max_digits=5, decimal_places=2
                "aqi": safe_int(row.get("AQI")),
            }
        except Exception as e:
            logger.error(f"Error processing row: {str(e)}")
            raise
