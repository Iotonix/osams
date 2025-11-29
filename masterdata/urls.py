from django.urls import path
from .views import (
    # Airlines
    airline_list,
    add_airline,
    edit_airline,
    delete_airline,
    # Airports
    airport_list,
    add_airport,
    edit_airport,
    delete_airport,
    # Aircraft
    aircraft_list,
    add_aircraft,
    edit_aircraft,
    delete_aircraft,
    # Terminals
    terminal_list,
    add_terminal,
    edit_terminal,
    delete_terminal,
    # Gates
    gate_list,
    add_gate,
    edit_gate,
    delete_gate,
    # Stands
    stand_list,
    add_stand,
    edit_stand,
    delete_stand,
    # Check-in Counters
    checkin_list,
    add_checkin,
    edit_checkin,
    delete_checkin,
    # Baggage Carousels
    carousel_list,
    add_carousel,
    edit_carousel,
    delete_carousel,
)

app_name = "masterdata"

urlpatterns = [
    # Airlines
    path("airlines/", airline_list, name="airline_list"),
    path("airlines/add/", add_airline, name="add_airline"),
    path("airlines/<int:pk>/edit/", edit_airline, name="edit_airline"),
    path("airlines/<int:pk>/delete/", delete_airline, name="delete_airline"),
    # Airports
    path("airports/", airport_list, name="airport_list"),
    path("airports/add/", add_airport, name="add_airport"),
    path("airports/<int:pk>/edit/", edit_airport, name="edit_airport"),
    path("airports/<int:pk>/delete/", delete_airport, name="delete_airport"),
    # Aircraft Types
    path("aircraft/", aircraft_list, name="aircraft_list"),
    path("aircraft/add/", add_aircraft, name="add_aircraft"),
    path("aircraft/<int:pk>/edit/", edit_aircraft, name="edit_aircraft"),
    path("aircraft/<int:pk>/delete/", delete_aircraft, name="delete_aircraft"),
    # Terminals
    path("terminals/", terminal_list, name="terminal_list"),
    path("terminals/add/", add_terminal, name="add_terminal"),
    path("terminals/<int:pk>/edit/", edit_terminal, name="edit_terminal"),
    path("terminals/<int:pk>/delete/", delete_terminal, name="delete_terminal"),
    # Gates
    path("gates/", gate_list, name="gate_list"),
    path("gates/add/", add_gate, name="add_gate"),
    path("gates/<int:pk>/edit/", edit_gate, name="edit_gate"),
    path("gates/<int:pk>/delete/", delete_gate, name="delete_gate"),
    # Stands
    path("stands/", stand_list, name="stand_list"),
    path("stands/add/", add_stand, name="add_stand"),
    path("stands/<int:pk>/edit/", edit_stand, name="edit_stand"),
    path("stands/<int:pk>/delete/", delete_stand, name="delete_stand"),
    # Check-in Counters
    path("checkin/", checkin_list, name="checkin_list"),
    path("checkin/add/", add_checkin, name="add_checkin"),
    path("checkin/<int:pk>/edit/", edit_checkin, name="edit_checkin"),
    path("checkin/<int:pk>/delete/", delete_checkin, name="delete_checkin"),
    # Baggage Carousels
    path("carousels/", carousel_list, name="carousel_list"),
    path("carousels/add/", add_carousel, name="add_carousel"),
    path("carousels/<int:pk>/edit/", edit_carousel, name="edit_carousel"),
    path("carousels/<int:pk>/delete/", delete_carousel, name="delete_carousel"),
]
