from django import forms
from django.db import models
from django.core.cache import cache
from .models import DailyFlight


class BootstrapFormMixin:
    """Mixin to add Bootstrap classes to form fields"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            elif isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs["class"] = "form-select"
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["rows"] = 3
            else:
                field.widget.attrs["class"] = "form-control"


def get_cached_used_ids():
    """Get cached IDs of airlines/airports/aircraft actually used in DailyFlights"""
    cache_key = 'dailyflight_form_ids'
    cached = cache.get(cache_key)
    
    if cached:
        return cached
    
    # Query once and cache for 5 minutes
    airline_ids = list(DailyFlight.objects.values_list("airline_id", flat=True).distinct())
    aircraft_ids = list(DailyFlight.objects.values_list("aircraft_type_id", flat=True).distinct())
    origin_ids = list(DailyFlight.objects.values_list("origin_id", flat=True).distinct())
    dest_ids = list(DailyFlight.objects.values_list("destination_id", flat=True).distinct())
    airport_ids = list(set(origin_ids) | set(dest_ids))
    
    result = {
        'airline_ids': airline_ids,
        'aircraft_ids': aircraft_ids,
        'airport_ids': airport_ids,
    }
    
    cache.set(cache_key, result, 300)  # Cache for 5 minutes
    return result


class DailyFlightForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = DailyFlight
        fields = [
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
            "stod",
            "etod",
            "aobt",
            "atod",
            "stoa",
            "etoa",
            "atoa",
            "aibt",
            "gate",
            "stand",
            "checkin_counters",
            "carousel",
            "public_remark",
            "qr_code_data",
        ]
        widgets = {
            "date_of_operation": forms.DateInput(attrs={"type": "date"}),
            "stod": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "etod": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "aobt": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "atod": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "stoa": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "etoa": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "atoa": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "aibt": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "qr_code_data": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # AGGRESSIVE optimization with caching - only load records actually used
        from masterdata.models import Airline, Airport, AircraftType, Gate, Stand, CheckInCounter, BaggageCarousel

        # Get cached IDs (avoids repeated slow queries)
        ids = get_cached_used_ids()
        
        # Load ONLY the records actually used (94 airlines instead of 831, 122 airports instead of 6067)
        self.fields["airline"].queryset = Airline.objects.filter(id__in=ids['airline_ids'])
        self.fields["aircraft_type"].queryset = AircraftType.objects.filter(id__in=ids['aircraft_ids'])
        self.fields["origin"].queryset = Airport.objects.filter(id__in=ids['airport_ids'])
        self.fields["destination"].queryset = self.fields["origin"].queryset

        # Resources - load all (small sets: 38 gates, 20 stands, etc.)
        self.fields["gate"].queryset = Gate.objects.filter(is_active=True)
        self.fields["stand"].queryset = Stand.objects.filter(is_active=True)
        self.fields["checkin_counters"].queryset = CheckInCounter.objects.filter(is_active=True)
        self.fields["carousel"].queryset = BaggageCarousel.objects.filter(is_active=True)
