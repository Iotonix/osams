from django.db import models


# Create your models here.
class SeasonalFlight(models.Model):
    """
    Represents a flight series (e.g., TG920 flies Mon/Wed/Fri from Oct to Mar).
    Corresponds to SSIM Type 3/4 records.
    """

    airline = models.ForeignKey("masterdata.Airline", on_delete=models.CASCADE)
    flight_number = models.CharField(max_length=10)  # e.g. "920"

    # "HOPO" (Home Port) logic is handled by relation to our airport
    origin = models.ForeignKey("masterdata.Airport", related_name="dep_schedules", on_delete=models.CASCADE)
    destination = models.ForeignKey("masterdata.Airport", related_name="arr_schedules", on_delete=models.CASCADE)

    # Equipment
    aircraft_type = models.ForeignKey("masterdata.AircraftType", on_delete=models.CASCADE)
    service_type = models.CharField(max_length=1, default="J")  # J=Scheduled Passenger, F=Cargo...

    # Timing (Local or UTC? Usually UTC for system, Local for display)
    stod = models.TimeField(help_text="Scheduled Time of Departure")
    stoa = models.TimeField(help_text="Scheduled Time of Arrival")

    # Validity & Frequency
    start_date = models.DateField()
    end_date = models.DateField()
    days_of_operation = models.CharField(max_length=7, help_text="MTWTFSS e.g., 1234567")

    class Meta:
        unique_together = ("airline", "flight_number", "start_date")


# osams/flight_ops/models.py
