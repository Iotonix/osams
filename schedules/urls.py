from django.urls import path

from .views import (
    add_seasonal_flight,
    delete_seasonal_flight,
    edit_seasonal_flight,
    seasonal_flight_list,
    seasonal_gantt_view,
    seasonal_gantt_data,
)

app_name = "schedules"

urlpatterns = [
    # Seasonal Flights
    path("seasonal-flights/", seasonal_flight_list, name="seasonal_flight_list"),
    path("seasonal-flights/add/", add_seasonal_flight, name="add_seasonal_flight"),
    path("seasonal-flights/<int:pk>/edit/", edit_seasonal_flight, name="edit_seasonal_flight"),
    path("seasonal-flights/<int:pk>/delete/", delete_seasonal_flight, name="delete_seasonal_flight"),
    path("seasonal-flights/gantt/", seasonal_gantt_view, name="seasonal_gantt"),
    path("api/seasonal-gantt-data/", seasonal_gantt_data, name="seasonal_gantt_data"),
]
