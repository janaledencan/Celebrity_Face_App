from django.urls import path

from . import views

app_name = "faceapp"

urlpatterns = [
    path("get_prediction", views.get_prediction, name="get_prediction"),
    path("user_data_submit", views.post_user_data, name="post_user_data"),
    path("", views.home, name="home"),
]