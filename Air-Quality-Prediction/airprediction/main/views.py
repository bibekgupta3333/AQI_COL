import csv
import random
import datetime
import pandas as pd
from django.contrib import auth
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Dataset, Dataset1, Dataset2, Dataset3

def load_data():
    csv_reader = csv.reader(
        open(
            "/home/bibekg/Learning/AQI/Air-Quality-Prediction/airquality/airprediction/main/data.csv"
        )
    )
    for row in csv_reader:
        print(row[5], row[6], row[7])
        if "2018" in row[5] and "o3" in row[6]:
            Dataset(
                date=row[5],
                Ozone=row[7],
                Pm25=0,
            ).save()

        if "2018" in row[5] and "pm25" in row[6]:
            Dataset(
                date=row[5],
                Ozone=0,
                Pm25=row[7],
            ).save()
        if "2019" in row[5] and "o3" in row[6]:
            Dataset1(
                date=row[5],
                Ozone=row[7],
                Pm25=0,
            ).save()

        if "2019" in row[5] and "pm25" in row[6]:
            Dataset1(
                date=row[5],
                Ozone=0,
                Pm25=row[7],
            ).save()
        if "2020" in row[5] and "o3" in row[6]:
            Dataset2(
                date=row[5],
                Ozone=row[7],
                Pm25=0,
            ).save()

        if "2020" in row[5] and "pm25" in row[6]:
            Dataset2(
                date=row[5],
                Ozone=0,
                Pm25=row[7],
            ).save()
        if "2021" in row[5] and "o3" in row[6]:
            Dataset3(
                date=row[5],
                Ozone=row[7],
                Pm25=0,
            ).save()

        if "2021" in row[5] and "pm25" in row[6]:
            Dataset3(
                date=row[5],
                Ozone=0,
                Pm25=row[7],
            ).save()


def homepage(request):
    import json
    import requests

    api_request = requests.get(
        "http://www.airnowapi.org/aq/observation/latLong/current/?format=application/json&latitude=27.700769&longitude=85.300140&distance=25&API_KEY=7AC96E40-0D38-49D2-A5FF-0240E15F336E"
    )

    city = "kathmandu"
    api_url = "https://api.api-ninjas.com/v1/airquality?city={}".format(city)
    response = requests.get(
        api_url, headers={"X-Api-Key": "XxyWnaye9xjgonImv4QiHA==BPxPDdb1hJx1DlAk"}
    )
    ninjaApiO3=0
    print("response",response.json(),"responseEnd",response.status_code)
    if response.status_code == requests.codes.ok:
        print("response",response.json(),"responseEnd",response.status_code)
        api = json.loads(response.text)
        {"CO": {"concentration": 694.28, "aqi": 7}, "NO2": {"concentration": 15.25, "aqi": 19}, "O3": {"concentration": 18.6, "aqi": 15}, "SO2": {"concentration": 6.26, "aqi": 9}, "PM2.5": {"concentration": 21.84, "aqi": 62}, "PM10": {"concentration": 30.46, "aqi": 28}, "overall_aqi": 62}
        ninjaApiO3=api["O3"]["aqi"]

        print(api["O3"])
    else:
        print("Error:", response.status_code, response.text)
    try:
        # api = json.loads(api_request.content)
        api = json.loads(api_request.content)
        print(api)
    except Exception as e:
        api = "error...."


    if api[0]["Category"]["Name"] == "Good":
        Category_Description = "(0-50) Air quality is satisfactory, and air pollution poses little or no risk."
        Category_color = "good"
    elif api[0]["Category"]["Name"] == "Moderate":
        Category_Description = "(51-100) Air quality is acceptable. However, there may be a risk for some people,particularly those who are unusually sensitive to air pollution."
        Category_color = "moderate"
    elif api[0]["Category"]["Name"] == "Unhealthy for Sensitive Groups":
        Category_Description = "(101-150) Members of sensitive groups may experience health effects. The general public is less likely to be affected."
        Category_color = "Unhealthy_for_Sensitive_Groups"
    elif api[0]["Category"]["Name"] == "Unhealthy":
        Category_Description = "(151-200) Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."
        Category_color = "Unhealthy"
    elif api[0]["Category"]["Name"] == "Very Unhealthy":
        Category_Description = "(201-300) Health alert: The risk of health effects is increased for everyone."
        Category_color = "Very_Unhealthy"
    elif api[0]["Category"]["Name"] == "Hazardous":
        Category_Description = "(301 and higher) Health warning of emergency conditions: everyone is more likely to be affected."
        Category_color = "Hazardous"
    print("NinjaAPI",ninjaApiO3)
    if ninjaApiO3 <= 50:
        Category_Description1 = "(0-50) Air quality is satisfactory, and air pollution poses little or no risk."
        Category_color1 = "good"
    elif ninjaApiO3 > 50  and ninjaApiO3 <= 100:
        Category_Description1 = "(51-100) Air quality is acceptable. However, there may be a risk for some people,particularly those who are unusually sensitive to air pollution."
        Category_color1 = "moderate"
    elif ninjaApiO3 > 100  and ninjaApiO3 <= 200:
        Category_Description1 = "(101-150) Members of sensitive groups may experience health effects. The general public is less likely to be affected."
        Category_color1 = "Unhealthy_for_Sensitive_Groups"
    elif ninjaApiO3 > 200:
        Category_Description1 = "(200- 500) Members of sensitive groups may experience health effects. The general public is less likely to be affected."
        Category_color1 = "Unhealthy_for_Sensitive_Groups"

    return render(
        request,
        "main/homepage.html",
        {
            "api": api,
            "ozone3": ninjaApiO3,
            "Category_Description": Category_Description,
            "Category_color": Category_color,
            "Category_Description1": Category_Description1,
            "Category_color1": Category_color1,
        },
    )


def about(request):
    return render(request, "main/about.html")


def past_data(request):
    if request.method == "POST":
        first = {}
        second = {}
        third = {}
        fourth = {}
        first["first"] = request.POST.get("first")
        second["second"] = request.POST.get("second")
        third["third"] = request.POST.get("third")
        fourth["fourth"] = request.POST.get("fourth")
        if first["first"]:
            data = Dataset.objects.all()
            return render(request, "main/past_data.html", {"data": data})
        elif second["second"]:
            data1 = Dataset1.objects.all()
            return render(request, "main/past_data.html", {"data1": data1})
        elif third["third"]:
            data2 = Dataset2.objects.all()
            return render(request, "main/past_data.html", {"data2": data2})
        elif fourth["fourth"]:
            data3 = Dataset3.objects.all()
            return render(request, "main/past_data.html", {"data3": data3})
        else:
            return render(request, "main/past_data.html")
    else:
        return render(request, "main/past_data.html")


def predict(request):
    return render(request, "main/predict.html")


def predictaqinew(request):
    if not request.user.is_authenticated:
        return redirect("/")
    import pickle
    import numpy as np
    import os
    model_path = os.path.dirname(os.path.abspath(__file__)) +'/model.pkl'
    print(model_path)
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
        print(request)
        if request.method == "POST":
            print(request.POST)
            data={'T': float(request.POST.get('T')), 'TM': float(request.POST.get('TM')), 'Tm': float(request.POST.get('Tm')), 'SLP': float(request.POST.get('SLP')), 'H':  float(request.POST.get('H')), 'VV':  float(request.POST.get('VV')), 'V': float(request.POST.get('V')), 'VM':  float(request.POST.get('VM'))}
            print([np.array(list(data.values()))])
            print(data)
            prediction = model.predict([np.array(list(data.values()))])
            output = prediction[0]
            print(output)
            actual = output
            if actual <= 50:
                color = "good"
                descp = "(0-50) Air quality is satisfactory, and air pollution poses little or no risk."
                name = "Good AQI"

            elif actual >= 50:
                color = "moderate"
                descp = "(51-100) Air quality is acceptable. However, there may be a risk for some people,particularly those who are unusually sensitive to air pollution."
                name = "Moderate AQI"

            context = {
                "prediction_text":output,
                "actual": actual,
                "color": color,
                "descp": descp,
                "name": name,
            }
            return render(request, "main/predictnew.html", context)

    return render(request, "main/predictnew.html", {})


def download(request):
    if not request.user.is_authenticated:
        return redirect("/")
    print(request.method)
    if request.method == "POST":
        csv_reader = csv.reader(
            open(
                "/home/bibekg/Learning/AQI/Air-Quality-Prediction/airprediction/Data/Real-Data/Real_Combine.csv"
            )
        )

        for row in csv_reader:
            print(row)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            "attachment:filename=book" + str(datetime.datetime.now()) + ".csv"
        )
        writer = csv.writer(response)
        writer.writerow(["T", "TM", "Tm", "SLP", "H", "VV", "V", "VM", "PM 2.5"])
        for row in csv_reader:
            print(row)
            writer.writerow(row)
        return response

    return render(request, "main/download.html")


def signup(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        if request.POST["Password"] == request.POST["Password1"]:
            try:
                user = User.objects.get(username=request.POST["Username"])
                return render(
                    request,
                    "main/signup.html",
                    {"error": "user already exits!"},
                )
            except User.DoesNotExist:
                user = User.objects.create_user(
                    request.POST["Username"], password=request.POST["Password"]
                )
                auth.login(request, user)
                return render(request, "main/login.html")
        else:
            return render(
                request,
                "main/signup.html",
                {"error": "Password must be matched!"},
            )

    else:
        return render(request, "main/signup.html")


def login(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        user = auth.authenticate(
            username=request.POST["Username"], password=request.POST["Password"]
        )
        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            return render(
                request,
                "main/login.html",
                {"error": "username or password is incorrect!"},
            )

    else:
        return render(request, "main/login.html")


def logout(request):
    if request.method == "POST":
        auth.logout(request)
        return redirect("/")
