from django.urls import path

from .views import (
    add_daily_flight,
    daily_flight_list,
    delete_daily_flight,
    edit_daily_flight,
)

app_name = "flight_ops"

urlpatterns = [
    # Daily Flights
    path("daily-flights/", daily_flight_list, name="daily_flight_list"),
    path("daily-flights/add/", add_daily_flight, name="add_daily_flight"),
    path("daily-flights/<int:pk>/edit/", edit_daily_flight, name="edit_daily_flight"),
    path("daily-flights/<int:pk>/delete/", delete_daily_flight, name="delete_daily_flight"),
]
