from django.db import models
from django.core.exceptions import ValidationError


class SeasonalFlight(models.Model):
    """
    Represents a flight series (e.g., TG920 flies Mon/Wed/Fri from Oct to Mar).
    Corresponds to SSIM Type 3/4 records.
    """

    airline = models.ForeignKey("masterdata.Airline", on_delete=models.CASCADE)
    flight_number = models.CharField(max_length=10, help_text="Flight number (e.g., 920)")

    # "HOPO" (Home Port) logic is handled by relation to our airport
    origin = models.ForeignKey("masterdata.Airport", related_name="dep_schedules", on_delete=models.CASCADE)
    destination = models.ForeignKey("masterdata.Airport", related_name="arr_schedules", on_delete=models.CASCADE)

    # Equipment
    aircraft_type = models.ForeignKey("masterdata.AircraftType", on_delete=models.CASCADE)
    service_type = models.CharField(max_length=1, default="J", help_text="J=Scheduled Passenger, F=Cargo")

    # Timing (All times in UTC)
    stod = models.TimeField(help_text="Scheduled Time of Departure (UTC)")
    stoa = models.TimeField(help_text="Scheduled Time of Arrival (UTC)")

    # Validity & Frequency
    start_date = models.DateField(help_text="Season start date")
    end_date = models.DateField(help_text="Season end date")
    days_of_operation = models.CharField(max_length=7, help_text="Days: 1=Mon, 2=Tue... 7=Sun (e.g., 1357 for Mon/Wed/Fri/Sun)")

    # Preferred Resource Allocation (Template for Daily Operations)
    preferred_gate = models.ForeignKey(
        "masterdata.Gate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="seasonal_flights",
        help_text="The standard gate negotiated for this flight series (validated against aircraft compatibility)",
    )

    preferred_stand = models.ForeignKey(
        "masterdata.Stand",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="seasonal_flights",
        help_text="Parking position if gate is not available or for cargo/long layovers",
    )

    preferred_carousel = models.ForeignKey(
        "masterdata.BaggageCarousel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="seasonal_flights",
        help_text="Default baggage claim carousel for arrivals",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("airline", "flight_number", "start_date")
        ordering = ["airline", "flight_number", "start_date"]
        verbose_name = "Seasonal Flight"
        verbose_name_plural = "Seasonal Flights"

    def __str__(self):
        return f"{self.airline.iata_code}{self.flight_number} ({self.origin.iata_code}-{self.destination.iata_code})"

    def clean(self):
        """
        Validate static constraints for preferred resource allocation.
        Hard constraints (physical impossibilities) raise ValidationError.
        Soft constraints (operational preferences) add warnings to a list.
        """
        super().clean()
        errors = {}
        warnings = []

        # === HARD CONSTRAINT 1: Aircraft Type Compatibility (Gate) ===
        if self.preferred_gate and self.aircraft_type:
            # Check if gate restricts aircraft types
            allowed_types = self.preferred_gate.allowed_aircraft_types.all()
            if allowed_types.exists():
                if self.aircraft_type not in allowed_types:
                    errors["preferred_gate"] = f"Aircraft type {self.aircraft_type.icao_code} is not allowed on Gate {self.preferred_gate.code}. Allowed types: {', '.join([t.icao_code for t in allowed_types])}"

        # === HARD CONSTRAINT 2: Wingspan Restriction (Gate) ===
        if self.preferred_gate and self.aircraft_type:
            if self.preferred_gate.max_wingspan_meters:
                if self.aircraft_type.wingspan_meters > self.preferred_gate.max_wingspan_meters:
                    errors["preferred_gate"] = f"Aircraft wingspan ({self.aircraft_type.wingspan_meters}m) exceeds gate maximum ({self.preferred_gate.max_wingspan_meters}m)"

        # === HARD CONSTRAINT 3: Wingspan Restriction (Stand) ===
        if self.preferred_stand and self.aircraft_type:
            if self.preferred_stand.max_wingspan_meters:
                if self.aircraft_type.wingspan_meters > self.preferred_stand.max_wingspan_meters:
                    errors["preferred_stand"] = f"Aircraft wingspan ({self.aircraft_type.wingspan_meters}m) exceeds stand maximum ({self.preferred_stand.max_wingspan_meters}m)"

        # === SOFT CONSTRAINT: Terminal Matching (Warning Only) ===
        # Note: We don't have terminal context on SeasonalFlight directly,
        # but we can check if gate/carousel are in the same terminal
        if self.preferred_gate and self.preferred_carousel:
            if self.preferred_gate.terminal != self.preferred_carousel.terminal:
                warnings.append(
                    f"Warning: Gate {self.preferred_gate.code} is in {self.preferred_gate.terminal.code}, "
                    f"but Carousel {self.preferred_carousel.code} is in {self.preferred_carousel.terminal.code}. "
                    f"This may require passenger transfer between terminals."
                )

        # Raise validation errors for hard constraints
        if errors:
            raise ValidationError(errors)

        # Store warnings for display (Django doesn't have built-in warning system in clean())
        # In production, you might want to use Django messages framework in the admin
        if warnings:
            # For now, we'll add warnings to a non-field error
            # Admin can display these with custom form handling
            pass  # Warnings are informational only and don't block saving
