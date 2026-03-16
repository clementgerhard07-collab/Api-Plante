from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload, name="upload"),
    path("identify/", views.analyse_plante, name="identify"),
    path('', views.analyse_plante, name='analyse_plante'),
]