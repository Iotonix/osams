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
        "is_manually_modified",
        "registration",
        "gate",
        "stand",
    ]
    list_filter = ["status", "is_manually_modified", "airline", "date_of_operation", "origin", "destination"]
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

    actions = ["propagate_from_schedule"]

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
        (
            "Rolling Window Strategy",
            {
                "fields": ("is_manually_modified", "schedule_version", "last_propagated_at"),
                "classes": ["collapse"],
            },
        ),
        ("Departure Times", {"fields": ("stod", "etod", "aobt", "atod")}),
        ("Arrival Times", {"fields": ("stoa", "etoa", "atoa", "aibt")}),
        ("Resource Allocation", {"fields": ("gate", "stand", "checkin_counters", "carousel")}),
        ("Additional Information", {"fields": ("public_remark", "qr_code_data")}),
    )

    readonly_fields = ["schedule_version", "last_propagated_at"]

    def save_model(self, request, obj, form, change):
        """Mark as manually modified when edited through admin"""
        if change:  # Only on edit, not create
            obj.is_manually_modified = True
        super().save_model(request, obj, form, change)

    def propagate_from_schedule(self, request, queryset):
        """Admin action to propagate schedule changes to selected flights"""
        from django.utils import timezone
        from datetime import datetime, timedelta

        updated = 0
        skipped = 0

        for daily_flight in queryset:
            if daily_flight.is_manually_modified:
                skipped += 1
                continue

            if not daily_flight.schedule:
                skipped += 1
                continue

            schedule = daily_flight.schedule

            # Update from schedule
            new_stod = timezone.make_aware(datetime.combine(daily_flight.date_of_operation, schedule.stod))
            new_stoa = timezone.make_aware(datetime.combine(daily_flight.date_of_operation, schedule.stoa))

            if schedule.stoa < schedule.stod:
                new_stoa = timezone.make_aware(datetime.combine(daily_flight.date_of_operation + timedelta(days=1), schedule.stoa))

            daily_flight.stod = new_stod
            daily_flight.stoa = new_stoa
            daily_flight.aircraft_type = schedule.aircraft_type
            daily_flight.last_propagated_at = timezone.now()
            daily_flight.schedule_version += 1
            daily_flight.save()
            updated += 1

        self.message_user(request, f"Propagated {updated} flights. Skipped {skipped} (manually modified or no schedule).")

    propagate_from_schedule.short_description = "Propagate schedule changes to selected flights"
