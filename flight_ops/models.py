from django.db import models

# Create your models here.
# osams/schedules/models.py


class DailyFlight(models.Model):
    """
    Represents a specific flight operation on a specific date.
    """

    STATUS_CHOICES = [
        ("SCH", "Scheduled"),
        ("AIR", "Airborne"),
        ("LND", "Landed"),
        ("FIB", "First Bag"),
        ("LSB", "Last Bag"),
        ("ONB", "On Block"),
        ("OFB", "Off Block"),
        ("CXX", "Cancelled"),  # Your 'CXX'
        ("DIV", "Diverted"),
    ]

    # Link back to the Master Schedule
    schedule = models.ForeignKey("schedules.SeasonalFlight", on_delete=models.SET_NULL, null=True, blank=True)

    date_of_operation = models.DateField()
    flight_id = models.CharField(max_length=20, unique=True)  # YYYYMMDD... as per your schema

    # Aircraft (Specific to this day)
    registration = models.CharField(max_length=10, blank=True)

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
    public_remark = models.CharField(max_length=50, blank=True)  # e.g., "Go to Gate"

    # Real-time tracking
    qr_code_data = models.TextField(blank=True)  # Storing the data string, generate SVG in view

    def __str__(self):
        return f"{self.schedule.airline.iata_code}{self.schedule.flight_number} / {self.date_of_operation}"
