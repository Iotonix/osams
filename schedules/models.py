from django.db import models


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
