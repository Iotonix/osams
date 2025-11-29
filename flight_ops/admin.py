from django.contrib import admin

from .models import DailyFlight


@admin.register(DailyFlight)
class DailyFlightAdmin(admin.ModelAdmin):
    list_display = [
        "flight_id",
        "airline",
        "flight_number",
        "date_of_operation",
        "origin",
        "destination",
        "status",
        "registration",
        "gate",
        "stand",
    ]
    list_filter = ["status", "airline", "date_of_operation", "origin", "destination"]
    search_fields = [
        "flight_id",
        "flight_number",
        "airline__iata_code",
        "airline__name",
        "registration",
        "origin__iata_code",
        "destination__iata_code",
    ]
    ordering = ["-date_of_operation", "stod", "airline", "flight_number"]
    date_hierarchy = "date_of_operation"

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "schedule",
                    "airline",
                    "flight_number",
                    "origin",
                    "destination",
                    "aircraft_type",
                    "date_of_operation",
                    "flight_id",
                    "registration",
                    "status",
                )
            },
        ),
        ("Departure Times", {"fields": ("stod", "etod", "aobt", "atod")}),
        ("Arrival Times", {"fields": ("stoa", "etoa", "atoa", "aibt")}),
        ("Resource Allocation", {"fields": ("gate", "stand", "checkin_counters", "carousel")}),
        ("Additional Information", {"fields": ("public_remark", "qr_code_data")}),
    )
