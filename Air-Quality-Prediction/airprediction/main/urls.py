
from django.urls import path
from . import views


app_name = "main"

urlpatterns = [
    path("", views.homepage, name="home-page"),
    path("about", views.about, name="about-us"),
    path("past_data", views.past_data, name="past-data"),
    path("predict", views.predict, name="predict-data"),
    path("predictaqi", views.predictaqinew, name="predict-aqi"),
    path("signup", views.signup, name="signup"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("download", views.download, name="download"),
]
