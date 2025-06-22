"""
Django management command to load AQI data from CSV files
Usage: python manage.py load_aqi_data
"""

import csv
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction

from main.models import AQIDataset, WeatherData

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load AQI data from CSV files into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-path',
            type=str,
            default=None,
            help='Path to CSV files directory (defaults to Data/AQI directory)'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Load specific CSV file'
        )
        parser.add_argument(
            '--year',
            type=int,
            choices=[2018, 2019, 2020, 2021, 2022, 2023],
            help='Load data for specific year'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be loaded without actually loading'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        try:
            # Determine CSV path
            csv_path = options.get('csv_path')
            if not csv_path:
                csv_path = Path(settings.BASE_DIR) / 'Data' / 'AQI'
            
            csv_path = Path(csv_path)
            
            if not csv_path.exists():
                raise CommandError(f"CSV path does not exist: {csv_path}")
            
            self.stdout.write(f"Looking for CSV files in: {csv_path}")
            
            # Clear existing data if requested
            if options['clear'] and not options['dry_run']:
                self.stdout.write("Clearing existing AQI data...")
                AQIDataset.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS("Existing data cleared.")
                )
            
            # Load specific file or all files
            if options['file']:
                file_path = csv_path / options['file']
                if file_path.exists():
                    self.load_csv_file(file_path, options)
                else:
                    raise CommandError(f"File not found: {file_path}")
            else:
                self.load_all_csv_files(csv_path, options)
            
            if not options['dry_run']:
                self.stdout.write(
                    self.style.SUCCESS("Data loading completed successfully!")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("Dry run completed - no data was actually loaded.")
                )
                
        except Exception as e:
            logger.error(f"Error in load_aqi_data command: {str(e)}")
            raise CommandError(f"Command failed: {str(e)}")

    def load_all_csv_files(self, csv_path: Path, options: Dict):
        """Load all CSV files in the directory"""
        csv_files = list(csv_path.glob('*.csv'))
        
        if not csv_files:
            self.stdout.write(
                self.style.WARNING(f"No CSV files found in {csv_path}")
            )
            return
        
        self.stdout.write(f"Found {len(csv_files)} CSV files:")
        for csv_file in csv_files:
            self.stdout.write(f"  - {csv_file.name}")
        
        for csv_file in csv_files:
            # Filter by year if specified
            if options['year']:
                if str(options['year']) not in csv_file.name:
                    continue
            
            self.load_csv_file(csv_file, options)

    def load_csv_file(self, file_path: Path, options: Dict):
        """Load data from a single CSV file"""
        self.stdout.write(f"\nProcessing: {file_path.name}")
        
        # Extract year from filename
        year = self.extract_year_from_filename(file_path.name)
        if not year:
            self.stdout.write(
                self.style.WARNING(f"Could not extract year from filename: {file_path.name}")
            )
            return
        
        try:
            records_processed = 0
            records_created = 0
            daily_data = defaultdict(list)  # Group hourly data by date
            errors = []
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Show headers
                self.stdout.write(f"CSV headers: {list(reader.fieldnames)}")
                
                if options['dry_run']:
                    # Just show first few rows
                    for i, row in enumerate(reader):
                        if i >= 5:  # Show first 5 rows
                            break
                        self.stdout.write(f"Row {i+1}: {dict(row)}")
                    return
                
                # Read all hourly data first
                for row_num, row in enumerate(reader, start=2):
                    try:
                        processed_row = self.process_csv_row(row, year)
                        if processed_row:
                            date_key = processed_row['date']
                            daily_data[date_key].append(processed_row['pm25'])
                        records_processed += 1
                        
                        # Show progress every 1000 records
                        if records_processed % 1000 == 0:
                            self.stdout.write(f"  Processed {records_processed} records...")
                            
                    except Exception as e:
                        error_msg = f"Row {row_num}: {str(e)}"
                        errors.append(error_msg)
                        if len(errors) <= 10:  # Show first 10 errors
                            self.stdout.write(
                                self.style.WARNING(f"  Error in {error_msg}")
                            )
                
                # Now create daily averages and save to database
                with transaction.atomic():
                    for date_str, pm25_values in daily_data.items():
                        try:
                            # Filter out None values and calculate average
                            valid_values = [v for v in pm25_values if v is not None]
                            if valid_values:
                                avg_pm25 = sum(valid_values) / len(valid_values)
                                
                                # Create or update record
                                aqi_record, created = AQIDataset.objects.get_or_create(
                                    date=date_str,
                                    location='Kathmandu',
                                    defaults={
                                        'year': year,
                                        'pm25': round(avg_pm25, 2),
                                        'ozone': None,  # Will be added later if available
                                    }
                                )
                                
                                if not created and aqi_record.pm25 != avg_pm25:
                                    aqi_record.pm25 = round(avg_pm25, 2)
                                    aqi_record.save()
                                
                                if created:
                                    records_created += 1
                                    
                        except Exception as e:
                            error_msg = f"Date {date_str}: {str(e)}"
                            errors.append(error_msg)
            
            # Summary
            self.stdout.write(
                self.style.SUCCESS(
                    f"  Completed: {records_processed} hourly records processed, "
                    f"{len(daily_data)} daily records, {records_created} new records created, "
                    f"{len(errors)} errors"
                )
            )
            
            if errors and len(errors) > 10:
                self.stdout.write(
                    self.style.WARNING(f"  ... and {len(errors) - 10} more errors")
                )
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise CommandError(f"Failed to process {file_path}: {str(e)}")

    def process_csv_row(self, row: Dict, year: int) -> Dict:
        """Process a single CSV row and return parsed data"""
        try:
            # Get date and time
            date_str = row.get('Date', '').strip()
            time_str = row.get('Time', '').strip()
            pm25_str = row.get('PM2.5', '').strip()
            
            if not date_str:
                return None
            
            # Parse date - handle different formats
            date_obj = None
            date_formats = ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%m-%d-%Y']
            
            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
            
            if not date_obj:
                # Try to handle edge cases like "01/01/2021 24:00 AM"
                if ' ' in date_str:
                    date_part = date_str.split()[0]
                    for fmt in date_formats:
                        try:
                            date_obj = datetime.strptime(date_part, fmt).date()
                            break
                        except ValueError:
                            continue
            
            if not date_obj:
                logger.warning(f"Could not parse date: {date_str}")
                return None
            
            # Parse PM2.5 value
            pm25 = self.safe_float(pm25_str)
            
            return {
                'date': date_obj,
                'pm25': pm25,
                'year': year
            }
            
        except Exception as e:
            logger.error(f"Error processing row {row}: {str(e)}")
            raise

    def extract_year_from_filename(self, filename: str) -> int:
        """Extract year from filename"""
        import re
        
        # Look for 4-digit year in filename
        match = re.search(r'(20\d{2})', filename)
        if match:
            return int(match.group(1))
        
        return None

    def safe_float(self, value) -> float:
        """Safely convert value to float"""
        if value is None or value == '' or value == '---':
            return None
        
        try:
            # Handle negative values that might indicate missing data
            float_val = float(value)
            if float_val < 0:
                return None
            return float_val
        except (ValueError, TypeError):
            return None 