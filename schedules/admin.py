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
        "preferred_gate",
        "preferred_stand",
        "is_active",
    ]
    list_filter = ["airline", "origin", "destination", "is_active", "start_date"]
    search_fields = ["flight_number", "airline__iata_code", "airline__name", "origin__iata_code", "destination__iata_code"]
    ordering = ["airline", "flight_number", "start_date"]

    # Use autocomplete for foreign key fields to improve performance
    autocomplete_fields = ["airline", "origin", "destination", "aircraft_type", "preferred_gate", "preferred_stand", "preferred_carousel"]

    fieldsets = (
        (
            "Flight Information",
            {
                "fields": (
                    "airline",
                    "flight_number",
                    "origin",
                    "destination",
                    "aircraft_type",
                    "service_type",
                )
            },
        ),
        (
            "Schedule Timing (UTC)",
            {
                "fields": (
                    "stod",
                    "stoa",
                    "start_date",
                    "end_date",
                    "days_of_operation",
                )
            },
        ),
        (
            "Preferred Resource Allocation",
            {
                "fields": (
                    "preferred_gate",
                    "preferred_stand",
                    "preferred_carousel",
                ),
                "description": "These resources will be automatically assigned to daily flights during generation. "
                "Gate/Stand assignments are validated against aircraft compatibility.",
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",)
            },
        ),
    )
