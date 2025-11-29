from django.db import models


class DailyFlight(models.Model):
    """
    Represents a specific flight operation on a specific date.
    Generated from seasonal schedules or ad-hoc operations.
    """

    STATUS_CHOICES = [
        ("SCH", "Scheduled"),
        ("OFB", "Off Block"),
        ("AIR", "Airborne"),
        ("LND", "Landed"),
        ("ONB", "On Block"),
        ("FIB", "First Bag"),
        ("LSB", "Last Bag"),
        ("CXX", "Cancelled"),
        ("DIV", "Diverted"),
    ]

    # Link back to the Master Schedule
    schedule = models.ForeignKey(
        "schedules.SeasonalFlight", on_delete=models.SET_NULL, null=True, blank=True, help_text="Source seasonal flight (if applicable)"
    )

    # Basic Flight Info
    airline = models.ForeignKey("masterdata.Airline", on_delete=models.CASCADE)
    flight_number = models.CharField(max_length=10, help_text="Flight number (e.g., 920)")
    origin = models.ForeignKey("masterdata.Airport", related_name="daily_departures", on_delete=models.CASCADE)
    destination = models.ForeignKey("masterdata.Airport", related_name="daily_arrivals", on_delete=models.CASCADE)
    aircraft_type = models.ForeignKey("masterdata.AircraftType", on_delete=models.CASCADE)

    date_of_operation = models.DateField(help_text="Date of flight operation")
    flight_id = models.CharField(max_length=20, unique=True, help_text="Unique flight identifier (e.g., YYYYMMDD-XX123)")

    # Aircraft (Specific to this day)
    registration = models.CharField(max_length=10, blank=True, help_text="Aircraft registration (tail number)")

    # Status
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default="SCH")

    # DEPARTURE TIMINGS (The expertise fields)
    stod = models.DateTimeField(help_text="Scheduled Time of Departure")
    etod = models.DateTimeField(null=True, blank=True, help_text="Estimated Time of Departure")
    aobt = models.DateTimeField(null=True, blank=True, help_text="Actual Off-Block Time")  # Industry standard for 'offblock'
    atod = models.DateTimeField(null=True, blank=True, help_text="Actual Time of Departure (Wheels Up)")

    # ARRIVAL TIMINGS
    stoa = models.DateTimeField(help_text="Scheduled Time of Arrival")
    etoa = models.DateTimeField(null=True, blank=True, help_text="Estimated Time of Arrival")
    atoa = models.DateTimeField(null=True, blank=True, help_text="Actual Time of Arrival (Touchdown)")
    aibt = models.DateTimeField(null=True, blank=True, help_text="Actual In-Block Time")  # Industry standard for 'onblock'

    # Resources (Foreign Keys to your Master Data)
    gate = models.ForeignKey("masterdata.Gate", null=True, blank=True, on_delete=models.SET_NULL)
    stand = models.ForeignKey("masterdata.Stand", null=True, blank=True, on_delete=models.SET_NULL)
    checkin_counters = models.ManyToManyField("masterdata.CheckInCounter", blank=True)
    carousel = models.ForeignKey("masterdata.BaggageCarousel", null=True, blank=True, on_delete=models.SET_NULL)

    # FIDS
    public_remark = models.CharField(max_length=50, blank=True, help_text="Public display message (e.g., 'Go to Gate')")

    # Real-time tracking
    qr_code_data = models.TextField(blank=True, help_text="QR code data for mobile boarding")

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date_of_operation", "stod", "airline", "flight_number"]
        verbose_name = "Daily Flight"
        verbose_name_plural = "Daily Flights"
        indexes = [
            models.Index(fields=["date_of_operation", "airline"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.airline.iata_code}{self.flight_number} on {self.date_of_operation} ({self.origin.iata_code}-{self.destination.iata_code})"
