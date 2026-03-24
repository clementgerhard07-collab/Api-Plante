from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload, name='upload'),
    path("identify/", views.identify_plant, name="identify"),

]