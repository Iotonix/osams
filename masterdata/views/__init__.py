# Re-export all views for backward compatibility
from .airlines import airline_list, add_airline, edit_airline, delete_airline
from .airports import airport_list, add_airport, edit_airport, delete_airport
from .aircraft import aircraft_list, add_aircraft, edit_aircraft, delete_aircraft
from .terminals import terminal_list, add_terminal, edit_terminal, delete_terminal
from .gates import gate_list, add_gate, edit_gate, delete_gate
from .stands import stand_list, add_stand, edit_stand, delete_stand
from .checkin import checkin_list, add_checkin, edit_checkin, delete_checkin
from .carousels import carousel_list, add_carousel, edit_carousel, delete_carousel
from .groundhandlers import groundhandler_list, add_groundhandler, edit_groundhandler, delete_groundhandler
from .routes import route_list, add_route, edit_route, delete_route
from .runways import runway_list, add_runway, edit_runway, delete_runway

__all__ = [
    # Airlines
    "airline_list",
    "add_airline",
    "edit_airline",
    "delete_airline",
    # Airports
    "airport_list",
    "add_airport",
    "edit_airport",
    "delete_airport",
    # Aircraft
    "aircraft_list",
    "add_aircraft",
    "edit_aircraft",
    "delete_aircraft",
    # Terminals
    "terminal_list",
    "add_terminal",
    "edit_terminal",
    "delete_terminal",
    # Gates
    "gate_list",
    "add_gate",
    "edit_gate",
    "delete_gate",
    # Stands
    "stand_list",
    "add_stand",
    "edit_stand",
    "delete_stand",
    # Check-in Counters
    "checkin_list",
    "add_checkin",
    "edit_checkin",
    "delete_checkin",
    # Baggage Carousels
    "carousel_list",
    "add_carousel",
    "edit_carousel",
    "delete_carousel",
    # Ground Handlers
    "groundhandler_list",
    "add_groundhandler",
    "edit_groundhandler",
    "delete_groundhandler",
    # Routes
    "route_list",
    "add_route",
    "edit_route",
    "delete_route",
    # Runways
    "runway_list",
    "add_runway",
    "edit_runway",
    "delete_runway",
]
