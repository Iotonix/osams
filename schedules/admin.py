from django.contrib import admin

from .models import SeasonalFlight


@admin.register(SeasonalFlight)
class SeasonalFlightAdmin(admin.ModelAdmin):
    list_display = [
        "airline",
        "flight_number",
        "origin",
        "destination",
        "aircraft_type",
        "stod",
        "stoa",
        "start_date",
        "end_date",
        "days_of_operation",
        "is_active",
    ]
    list_filter = ["airline", "origin", "destination", "is_active", "start_date"]
    search_fields = ["flight_number", "airline__iata_code", "airline__name", "origin__iata_code", "destination__iata_code"]
    ordering = ["airline", "flight_number", "start_date"]
