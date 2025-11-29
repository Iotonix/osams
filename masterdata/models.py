from django.db import models
from django.core.validators import RegexValidator


class Airline(models.Model):
    """Airlines/Carriers operating at the airport"""

    iata_code = models.CharField(max_length=2, unique=True, validators=[RegexValidator(r"^[A-Z0-9]{2}$")], help_text="2-letter IATA code (e.g., TG, SQ)")
    icao_code = models.CharField(max_length=3, unique=True, validators=[RegexValidator(r"^[A-Z]{3}$")], help_text="3-letter ICAO code (e.g., THA, SIA)")
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["iata_code"]
        verbose_name = "Airline"
        verbose_name_plural = "Airlines"

    def __str__(self):
        return f"{self.iata_code} - {self.name}"


# masterdata/models.py


class Airport(models.Model):
    """Global airports reference data for Flight Schedules (Origin/Destination)"""

    iata_code = models.CharField(max_length=3, unique=True, validators=[RegexValidator(r"^[A-Z]{3}$")], help_text="3-letter IATA code (e.g., LHR, DXB)")
    icao_code = models.CharField(max_length=4, unique=True, validators=[RegexValidator(r"^[A-Z]{4}$")], help_text="4-letter ICAO code (e.g., EGLL, OMDB)")
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["iata_code"]
        verbose_name = "Airport"
        verbose_name_plural = "Airports"

    def __str__(self):
        return f"{self.iata_code} - {self.city} ({self.name})"


class AircraftType(models.Model):
    """Aircraft types and their specifications"""

    WAKE_TURBULENCE_CHOICES = [
        ("L", "Light"),
        ("M", "Medium"),
        ("H", "Heavy"),
        ("J", "Super (A380)"),
    ]

    SIZE_CATEGORY_CHOICES = [
        ("NB", "Narrow Body"),
        ("WB", "Wide Body"),
        ("RJ", "Regional Jet"),
    ]

    icao_code = models.CharField(
        max_length=4, unique=True, validators=[RegexValidator(r"^[A-Z0-9]{3,4}$")], help_text="ICAO aircraft type code (e.g., A320, B77W)"
    )
    iata_code = models.CharField(max_length=3, blank=True, null=True, help_text="IATA aircraft type code (e.g., 320, 777)")
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    wake_turbulence = models.CharField(max_length=1, choices=WAKE_TURBULENCE_CHOICES, default="M")
    size_category = models.CharField(max_length=2, choices=SIZE_CATEGORY_CHOICES, default="NB")
    wingspan_meters = models.DecimalField(max_digits=5, decimal_places=2, help_text="Wingspan in meters")
    length_meters = models.DecimalField(max_digits=5, decimal_places=2, help_text="Aircraft length in meters")
    max_takeoff_weight_kg = models.IntegerField(help_text="MTOW in kilograms")
    typical_capacity = models.IntegerField(help_text="Typical passenger capacity")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["icao_code"]
        verbose_name = "Aircraft Type"
        verbose_name_plural = "Aircraft Types"

    def __str__(self):
        return f"{self.icao_code} - {self.manufacturer} {self.model}"


class Terminal(models.Model):
    """Airport terminals/buildings"""

    code = models.CharField(max_length=10, unique=True, help_text="Terminal code (e.g., T1, T2, Domestic)")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Terminal"
        verbose_name_plural = "Terminals"

    def __str__(self):
        return f"{self.code} - {self.name}"


class Gate(models.Model):
    """Gates for passenger boarding"""

    GATE_TYPE_CHOICES = [
        ("CONTACT", "Contact Stand (Jetbridge)"),
        ("REMOTE", "Remote Stand (Bus)"),
        ("BOTH", "Flexible (Both)"),
    ]

    code = models.CharField(max_length=10, unique=True, help_text="Gate code (e.g., A1, B12, C3)")
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, related_name="gates")
    gate_type = models.CharField(max_length=10, choices=GATE_TYPE_CHOICES, default="CONTACT")
    allowed_aircraft_types = models.ManyToManyField(AircraftType, blank=True, help_text="Restrict gate to specific aircraft types (leave empty for all)")
    max_wingspan_meters = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Maximum wingspan restriction")
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True, help_text="Currently available for allocation")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Gate"
        verbose_name_plural = "Gates"

    def __str__(self):
        return f"{self.code} ({self.terminal.code})"


class Stand(models.Model):
    """Aircraft parking stands/aprons"""

    SIZE_CHOICES = [
        ("A", "Code A (Wingspan < 15m)"),
        ("B", "Code B (Wingspan 15-24m)"),
        ("C", "Code C (Wingspan 24-36m)"),
        ("D", "Code D (Wingspan 36-52m)"),
        ("E", "Code E (Wingspan 52-65m)"),
        ("F", "Code F (Wingspan 65-80m)"),
    ]

    code = models.CharField(max_length=10, unique=True, help_text="Stand code (e.g., R1, R2, A10)")
    size_code = models.CharField(max_length=1, choices=SIZE_CHOICES, default="C")
    max_wingspan_meters = models.DecimalField(max_digits=5, decimal_places=2, help_text="Maximum wingspan")
    has_pushback = models.BooleanField(default=True, help_text="Requires pushback (not self-maneuver)")
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Stand"
        verbose_name_plural = "Stands"

    def __str__(self):
        return f"{self.code} (Code {self.size_code})"


class CheckInCounter(models.Model):
    """Check-in counter desks"""

    code = models.CharField(max_length=10, unique=True, help_text="Counter code (e.g., A1, A2, B10-B15)")
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, related_name="checkin_counters")
    counter_group = models.CharField(max_length=50, blank=True, null=True, help_text="Group name (e.g., 'Row A', 'Island 1')")
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["terminal", "code"]
        verbose_name = "Check-in Counter"
        verbose_name_plural = "Check-in Counters"

    def __str__(self):
        return f"{self.code} ({self.terminal.code})"


class BaggageCarousel(models.Model):
    """Baggage claim carousels"""

    code = models.CharField(max_length=10, unique=True, help_text="Carousel code (e.g., C1, C2)")
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, related_name="baggage_carousels")
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["terminal", "code"]
        verbose_name = "Baggage Carousel"
        verbose_name_plural = "Baggage Carousels"

    def __str__(self):
        return f"{self.code} ({self.terminal.code})"


class Runway(models.Model):
    """Airport runways configurations"""

    SURFACE_CHOICES = [
        ("CONCRETE", "Concrete"),
        ("ASPHALT", "Asphalt"),
        ("GRASS", "Grass"),
    ]

    name = models.CharField(max_length=10, help_text="Designator (e.g., 09L/27R)")
    length_meters = models.IntegerField(help_text="Total length in meters")
    width_meters = models.IntegerField(help_text="Width in meters")
    surface = models.CharField(max_length=10, choices=SURFACE_CHOICES, default="CONCRETE")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Runway"
        verbose_name_plural = "Runways"

    def __str__(self):
        return f"Runway {self.name}"
