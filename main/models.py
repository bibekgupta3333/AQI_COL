from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime

# Improved models with better design and naming conventions


class AQIDataset(models.Model):
    """
    Consolidated model for all air quality data across different years
    """

    YEAR_CHOICES = [
        (2018, "2018"),
        (2019, "2019"),
        (2020, "2020"),
        (2021, "2021"),
        (2022, "2022"),
        (2023, "2023"),
    ]

    date = models.DateField()
    year = models.IntegerField(choices=YEAR_CHOICES, db_index=True)
    ozone = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    pm25 = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    location = models.CharField(max_length=120, default="Kathmandu")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ["date", "location"]
        indexes = [
            models.Index(fields=["date", "year"]),
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        return f"{self.location} - {self.date} (PM2.5: {self.pm25}, O3: {self.ozone})"


class WeatherData(models.Model):
    """
    Model for comprehensive weather and air quality data
    """

    date = models.DateField()
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=120, default="Kathmandu")

    # Temperature data
    temp_avg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # T
    temp_max = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # TM
    temp_min = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # Tm

    # Atmospheric data
    sea_level_pressure = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )  # SLP
    humidity = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )  # H
    visibility = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # VV

    # Wind data
    wind_speed = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # V
    wind_gust = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # VM

    # Air quality
    aqi = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(500)]
    )
    pm25 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    pm10 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    ozone = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    no2 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    co = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    so2 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-timestamp"]
        unique_together = ["date", "timestamp", "location"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["date"]),
            models.Index(fields=["location"]),
            models.Index(fields=["aqi"]),
        ]

    def __str__(self):
        return f"{self.location} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - AQI: {self.aqi}"

    def get_aqi_category(self):
        """Return AQI category and color based on AQI value"""
        if not self.aqi:
            return "Unknown", "gray"

        if self.aqi <= 50:
            return "Good", "green"
        elif self.aqi <= 100:
            return "Moderate", "yellow"
        elif self.aqi <= 150:
            return "Unhealthy for Sensitive Groups", "orange"
        elif self.aqi <= 200:
            return "Unhealthy", "red"
        elif self.aqi <= 300:
            return "Very Unhealthy", "purple"
        else:
            return "Hazardous", "maroon"


# Keep old models for backward compatibility but mark as deprecated
class Dataset(models.Model):
    """DEPRECATED: Use AQIDataset instead"""

    date = models.CharField(max_length=120)
    Ozone = models.DecimalField(max_digits=10, decimal_places=6, blank=False)
    Pm25 = models.DecimalField(max_digits=10, decimal_places=6, blank=False, null=True)

    class Meta:
        db_table = "main_dataset"


class Dataset1(models.Model):
    """DEPRECATED: Use AQIDataset instead"""

    date = models.CharField(max_length=120)
    Ozone = models.DecimalField(max_digits=10, decimal_places=6, blank=False)
    Pm25 = models.DecimalField(max_digits=10, decimal_places=6, blank=False, null=True)

    class Meta:
        db_table = "main_dataset1"


class Dataset2(models.Model):
    """DEPRECATED: Use AQIDataset instead"""

    date = models.CharField(max_length=120)
    Ozone = models.DecimalField(max_digits=10, decimal_places=6, blank=False)
    Pm25 = models.DecimalField(max_digits=10, decimal_places=6, blank=False, null=True)

    class Meta:
        db_table = "main_dataset2"


class Dataset3(models.Model):
    """DEPRECATED: Use AQIDataset instead"""

    date = models.CharField(max_length=120)
    Ozone = models.DecimalField(max_digits=10, decimal_places=6, blank=False)
    Pm25 = models.DecimalField(max_digits=10, decimal_places=6, blank=False, null=True)

    class Meta:
        db_table = "main_dataset3"
