from django.urls import path
from . import views

app_name = "masterdata"

urlpatterns = [
    path("airlines/", views.airline_list, name="airline_list"),
    path("aircraft/", views.aircraft_list, name="aircraft_list"),
    path("terminals/", views.terminal_list, name="terminal_list"),
    path("gates/", views.gate_list, name="gate_list"),
    path("stands/", views.stand_list, name="stand_list"),
    path("checkin/", views.checkin_list, name="checkin_list"),
    path("carousels/", views.carousel_list, name="carousel_list"),
]
