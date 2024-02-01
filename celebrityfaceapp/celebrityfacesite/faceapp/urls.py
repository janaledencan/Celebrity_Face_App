from django.urls import path

from . import views

app_name = "faceapp"

urlpatterns = [
    path("", views.home, name="home"),
]