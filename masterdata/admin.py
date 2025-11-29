from django.contrib import admin
from .models import Airline, AircraftType, Airport, Runway, Terminal, Gate, Stand, CheckInCounter, BaggageCarousel


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ["iata_code", "icao_code", "name", "country", "is_active"]
    list_filter = ["is_active", "country"]
    search_fields = ["iata_code", "icao_code", "name"]
    ordering = ["iata_code"]


@admin.register(AircraftType)
class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ["icao_code", "iata_code", "manufacturer", "model", "size_category", "wake_turbulence", "typical_capacity", "is_active"]
    list_filter = ["size_category", "wake_turbulence", "is_active", "manufacturer"]
    search_fields = ["icao_code", "iata_code", "manufacturer", "model"]
    ordering = ["icao_code"]


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ["iata_code", "icao_code", "name", "city", "country", "is_active"]
    list_filter = ["is_active", "country"]
    search_fields = ["iata_code", "icao_code", "name", "city"]
    ordering = ["iata_code"]


@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["code", "name"]
    ordering = ["code"]


@admin.register(Gate)
class GateAdmin(admin.ModelAdmin):
    list_display = ["code", "terminal", "gate_type", "is_active", "is_available"]
    list_filter = ["terminal", "gate_type", "is_active", "is_available"]
    search_fields = ["code"]
    filter_horizontal = ["allowed_aircraft_types"]
    ordering = ["code"]


@admin.register(Stand)
class StandAdmin(admin.ModelAdmin):
    list_display = ["code", "size_code", "max_wingspan_meters", "has_pushback", "is_active", "is_available"]
    list_filter = ["size_code", "has_pushback", "is_active", "is_available"]
    search_fields = ["code"]
    ordering = ["code"]


@admin.register(CheckInCounter)
class CheckInCounterAdmin(admin.ModelAdmin):
    list_display = ["code", "terminal", "counter_group", "is_active", "is_available"]
    list_filter = ["terminal", "is_active", "is_available"]
    search_fields = ["code", "counter_group"]
    ordering = ["terminal", "code"]


@admin.register(BaggageCarousel)
class BaggageCarouselAdmin(admin.ModelAdmin):
    list_display = ["code", "terminal", "is_active", "is_available"]
    list_filter = ["terminal", "is_active", "is_available"]
    search_fields = ["code"]
    ordering = ["terminal", "code"]


@admin.register(Runway)
class RunwayAdmin(admin.ModelAdmin):
    list_display = ["name", "length_meters", "width_meters", "surface", "is_active"]
    list_filter = ["surface", "is_active"]
    search_fields = ["name"]
    ordering = ["name"]
