from django.urls import path
from . import views


app_name = "main"

urlpatterns = [
    # Main pages
    path("", views.homepage, name="home-page"),
    path("about/", views.about, name="about-us"),
    
    # Data views
    path("past-data/", views.past_data, name="past-data"),
    path("predict/", views.predict, name="predict-data"),
    path("predict-aqi/", views.predictaqinew, name="predict-aqi"),
    path("download/", views.download, name="download"),
    
    # Authentication
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    
    # API endpoints
    path("api/current-aqi/", views.api_current_aqi, name="api-current-aqi"),
]
