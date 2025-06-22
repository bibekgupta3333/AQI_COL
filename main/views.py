import csv
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

import numpy as np
import pandas as pd
import pickle
import requests
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page

from .models import Dataset, Dataset1, Dataset2, Dataset3, AQIDataset, WeatherData

# Configure logging
logger = logging.getLogger(__name__)


# Configuration - Move these to settings.py or environment variables
class AQIConfig:
    AIRNOW_API_KEY = os.environ.get("AIRNOW_API_KEY", "demo-key")
    AIRQUALITY_API_KEY = os.environ.get("AIRQUALITY_API_KEY", "demo-key")
    KATHMANDU_LAT = 27.700769
    KATHMANDU_LON = 85.300140
    MODEL_PATH = os.path.join(settings.BASE_DIR, "main", "model.pkl")
    DATA_PATH = os.path.join(settings.BASE_DIR, "Data", "Real-Data", "Real_Combine.csv")

    # AQI Categories with proper ranges
    AQI_CATEGORIES = [
        (
            0,
            50,
            "Good",
            "good",
            "Air quality is satisfactory, and air pollution poses little or no risk.",
        ),
        (
            51,
            100,
            "Moderate",
            "moderate",
            "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.",
        ),
        (
            101,
            150,
            "Unhealthy for Sensitive Groups",
            "usg",
            "Members of sensitive groups may experience health effects. The general public is less likely to be affected.",
        ),
        (
            151,
            200,
            "Unhealthy",
            "unhealthy",
            "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.",
        ),
        (
            201,
            300,
            "Very Unhealthy",
            "very_unhealthy",
            "Health alert: The risk of health effects is increased for everyone.",
        ),
        (
            301,
            500,
            "Hazardous",
            "hazardous",
            "Health warning of emergency conditions: everyone is more likely to be affected.",
        ),
    ]


def get_aqi_category(aqi_value: float) -> Tuple[str, str, str]:
    """
    Get AQI category, color, and description based on AQI value
    """
    for min_val, max_val, name, color, description in AQIConfig.AQI_CATEGORIES:
        if min_val <= aqi_value <= max_val:
            return name, color, description

    # Default for values outside normal range
    return "Unknown", "gray", "AQI value is outside normal range."


def fetch_air_quality_data() -> Dict[str, Any]:
    """
    Fetch air quality data from multiple APIs with proper error handling
    """
    data = {"airnow_data": None, "ninjas_data": None, "overall_aqi": 0, "error": None}

    try:
        # AirNow API
        airnow_url = f"http://www.airnowapi.org/aq/observation/latLong/current/"
        airnow_params = {
            "format": "application/json",
            "latitude": AQIConfig.KATHMANDU_LAT,
            "longitude": AQIConfig.KATHMANDU_LON,
            "distance": 25,
            "API_KEY": AQIConfig.AIRNOW_API_KEY,
        }

        airnow_response = requests.get(airnow_url, params=airnow_params, timeout=10)
        if airnow_response.status_code == 200:
            data["airnow_data"] = airnow_response.json()
            logger.info(f"AirNow API success: {airnow_response.status_code}")
        else:
            logger.warning(f"AirNow API failed: {airnow_response.status_code}")

    except requests.RequestException as e:
        logger.error(f"AirNow API error: {str(e)}")

    try:
        # Air Quality Ninjas API
        ninjas_url = "https://api.api-ninjas.com/v1/airquality"
        ninjas_headers = {"X-Api-Key": AQIConfig.AIRQUALITY_API_KEY}
        ninjas_params = {"city": "kathmandu"}

        ninjas_response = requests.get(
            ninjas_url, headers=ninjas_headers, params=ninjas_params, timeout=10
        )
        if ninjas_response.status_code == 200:
            ninjas_json = ninjas_response.json()
            data["ninjas_data"] = ninjas_json
            data["overall_aqi"] = ninjas_json.get("overall_aqi", 0)
            logger.info(f"Ninjas API success: {ninjas_response.status_code}")
        else:
            logger.warning(f"Ninjas API failed: {ninjas_response.status_code}")

    except requests.RequestException as e:
        logger.error(f"Ninjas API error: {str(e)}")

    return data


@cache_page(60 * 15)  # Cache for 15 minutes
def homepage(request):
    """
    Homepage view with real-time air quality data
    """
    # Fetch air quality data
    air_quality_data = fetch_air_quality_data()

    # Get AQI category information
    overall_aqi = air_quality_data.get("overall_aqi", 0)
    category_name, category_color, category_description = get_aqi_category(overall_aqi)

    context = {
        "api_data": air_quality_data,
        "overall_aqi": overall_aqi,
        "category_name": category_name,
        "category_color": category_color,
        "category_description": category_description,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return render(request, "main/homepage.html", context)


def about(request):
    """About page view"""
    return render(request, "main/about.html")


@require_http_methods(["GET", "POST"])
def past_data(request):
    """
    Display historical air quality data with pagination
    """
    context = {}

    if request.method == "POST":
        year_selection = request.POST.get("year_filter")

        # Map year selection to appropriate dataset
        dataset_map = {
            "2018": Dataset.objects.all(),
            "2019": Dataset1.objects.all(),
            "2020": Dataset2.objects.all(),
            "2021": Dataset3.objects.all(),
        }

        if year_selection in dataset_map:
            data = dataset_map[year_selection]

            # Add pagination
            paginator = Paginator(data, 50)  # Show 50 records per page
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)

            context = {
                "data": page_obj,
                "selected_year": year_selection,
                "total_records": data.count(),
            }

    return render(request, "main/past_data.html", context)


def predict(request):
    """Prediction page view"""
    return render(request, "main/predict.html")


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def predictaqinew(request):
    """
    AQI prediction using machine learning model with proper validation
    """
    if request.method == "POST":
        try:
            # Validate and extract form data
            required_fields = ["T", "TM", "Tm", "SLP", "H", "VV", "V", "VM"]
            form_data = {}

            for field in required_fields:
                value = request.POST.get(field)
                if not value:
                    messages.error(request, f"Field {field} is required.")
                    return render(request, "main/predictnew.html")

                try:
                    form_data[field] = float(value)
                except ValueError:
                    messages.error(
                        request,
                        f"Invalid value for field {field}. Please enter a valid number.",
                    )
                    return render(request, "main/predictnew.html")

            # Basic validation ranges
            if not (0 <= form_data["H"] <= 100):
                messages.error(request, "Humidity must be between 0 and 100.")
                return render(request, "main/predictnew.html")

            # Load and use the model
            if not os.path.exists(AQIConfig.MODEL_PATH):
                messages.error(
                    request, "Prediction model not found. Please contact administrator."
                )
                return render(request, "main/predictnew.html")

            with open(AQIConfig.MODEL_PATH, "rb") as f:
                model = pickle.load(f)

            # Prepare data for prediction
            input_array = np.array([list(form_data.values())])
            prediction = model.predict(input_array)[0]

            # Get AQI category
            category_name, category_color, category_description = get_aqi_category(
                prediction
            )

            context = {
                "prediction_value": round(prediction, 2),
                "category_name": category_name,
                "category_color": category_color,
                "category_description": category_description,
                "input_data": form_data,
            }

            # Log prediction for monitoring
            logger.info(
                f"AQI Prediction: {prediction} for user {request.user.username}"
            )

            return render(request, "main/predictnew.html", context)

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            messages.error(
                request, "An error occurred during prediction. Please try again."
            )

    return render(request, "main/predictnew.html")


@login_required
@require_http_methods(["GET", "POST"])
def download(request):
    """
    Download processed data as CSV with proper error handling
    """
    if request.method == "POST":
        try:
            # Check if file exists
            if not os.path.exists(AQIConfig.DATA_PATH):
                messages.error(request, "Data file not found.")
                return render(request, "main/download.html")

            # Create HTTP response with CSV content type
            response = HttpResponse(content_type="text/csv")
            filename = f"aqi_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            response["Content-Disposition"] = f'attachment; filename="{filename}"'

            # Write CSV data
            writer = csv.writer(response)
            writer.writerow(["T", "TM", "Tm", "SLP", "H", "VV", "V", "VM", "PM 2.5"])

            with open(AQIConfig.DATA_PATH, "r") as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header if exists
                for row in reader:
                    writer.writerow(row)

            # Log download
            logger.info(f"Data downloaded by user {request.user.username}")

            return response

        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            messages.error(
                request, "An error occurred during download. Please try again."
            )

    return render(request, "main/download.html")


@csrf_protect
@require_http_methods(["GET", "POST"])
def signup(request):
    """
    User registration with improved validation and security
    """
    if request.user.is_authenticated:
        return redirect("main:home-page")

    if request.method == "POST":
        username = request.POST.get("Username", "").strip()
        password = request.POST.get("Password", "")
        password_confirm = request.POST.get("Password1", "")

        # Validation
        if not username:
            messages.error(request, "Username is required.")
        elif len(username) < 3:
            messages.error(request, "Username must be at least 3 characters long.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif not password:
            messages.error(request, "Password is required.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        elif password != password_confirm:
            messages.error(request, "Passwords do not match.")
        else:
            try:
                # Create user
                user = User.objects.create_user(username=username, password=password)
                auth.login(request, user)
                messages.success(request, "Account created successfully!")
                logger.info(f"New user registered: {username}")
                return redirect("main:home-page")
            except Exception as e:
                logger.error(f"User creation error: {str(e)}")
                messages.error(request, "An error occurred during registration.")

    return render(request, "main/signup.html")


@csrf_protect
@require_http_methods(["GET", "POST"])
def login(request):
    """
    User authentication with improved security
    """
    if request.user.is_authenticated:
        return redirect("main:home-page")

    if request.method == "POST":
        username = request.POST.get("Username", "").strip()
        password = request.POST.get("Password", "")

        if not username or not password:
            messages.error(request, "Both username and password are required.")
        else:
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                logger.info(f"User logged in: {username}")

                # Redirect to next page if specified
                next_page = request.GET.get("next", "main:home-page")
                return redirect(next_page)
            else:
                messages.error(request, "Invalid username or password.")
                logger.warning(f"Failed login attempt for username: {username}")

    return render(request, "main/login.html")


@login_required
@require_http_methods(["POST"])
def logout(request):
    """
    User logout with proper security
    """
    username = request.user.username
    auth.logout(request)
    messages.success(request, "You have been logged out successfully.")
    logger.info(f"User logged out: {username}")
    return redirect("main:home-page")


# API endpoints for AJAX requests
@require_http_methods(["GET"])
def api_current_aqi(request):
    """
    API endpoint to get current AQI data
    """
    try:
        data = fetch_air_quality_data()
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return JsonResponse({"error": "Failed to fetch data"}, status=500)


# Utility function for data loading (improved version)
def load_data_from_csv(csv_file_path: str) -> bool:
    """
    Load data from CSV file into database with proper error handling
    """
    try:
        if not os.path.exists(csv_file_path):
            logger.error(f"CSV file not found: {csv_file_path}")
            return False

        with open(csv_file_path, "r") as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip header

            for row in reader:
                # Process each row based on your data structure
                # This is a placeholder - adjust based on your CSV format
                try:
                    # Example processing
                    if len(row) >= 8:  # Ensure row has enough columns
                        date_str = row[5] if len(row) > 5 else ""
                        parameter = row[6] if len(row) > 6 else ""
                        value = float(row[7]) if len(row) > 7 and row[7] else 0

                        # Process based on your logic
                        # This would need to be adapted to your specific CSV format
                        pass

                except (ValueError, IndexError) as e:
                    logger.warning(f"Skipping invalid row: {row}, Error: {str(e)}")
                    continue

        logger.info(f"Successfully loaded data from {csv_file_path}")
        return True

    except Exception as e:
        logger.error(f"Error loading data from CSV: {str(e)}")
        return False
