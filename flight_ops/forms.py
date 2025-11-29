from django import forms
from django.db import models
from django.core.cache import cache
from django_select2 import forms as s2forms
from .models import DailyFlight


class BootstrapFormMixin:
    """Mixin to add Bootstrap classes to form fields"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Skip Select2 widgets - they have their own styling
            if isinstance(field.widget, (s2forms.ModelSelect2Widget, s2forms.ModelSelect2MultipleWidget)):
                continue
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
    cache_key = "dailyflight_form_ids"
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
        "airline_ids": airline_ids,
        "aircraft_ids": aircraft_ids,
        "airport_ids": airport_ids,
    }

    cache.set(cache_key, result, 300)  # Cache for 5 minutes
    return result


class DailyFlightForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = DailyFlight
        fields = [
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
        ]
        widgets = {
            # Use AJAX autocomplete for large dropdowns (fast loading)
            "airline": s2forms.ModelSelect2Widget(
                search_fields=["iata_code__icontains", "name__icontains"],
                attrs={
                    "data-minimum-input-length": 0,
                    "data-placeholder": "Select airline...",
                    "data-width": "100%",
                    "data-theme": "bootstrap-5",
                    "class": "form-control",
                },
            ),
            "origin": s2forms.ModelSelect2Widget(
                search_fields=["iata_code__icontains", "name__icontains", "city__icontains"],
                attrs={
                    "data-minimum-input-length": 0,
                    "data-placeholder": "Select origin airport...",
                    "data-width": "100%",
                    "data-theme": "bootstrap-5",
                    "class": "form-control",
                },
            ),
            "destination": s2forms.ModelSelect2Widget(
                search_fields=["iata_code__icontains", "name__icontains", "city__icontains"],
                attrs={
                    "data-minimum-input-length": 0,
                    "data-placeholder": "Select destination airport...",
                    "data-width": "100%",
                    "data-theme": "bootstrap-5",
                    "class": "form-control",
                },
            ),
            "aircraft_type": s2forms.ModelSelect2Widget(
                search_fields=["iata_code__icontains", "manufacturer__icontains", "model__icontains"],
                attrs={
                    "data-minimum-input-length": 0,
                    "data-placeholder": "Select aircraft type...",
                    "data-width": "100%",
                    "data-theme": "bootstrap-5",
                    "class": "form-control",
                },
            ),
            # Regular widgets for other fields
            "date_of_operation": forms.DateInput(attrs={"type": "date"}),
            "stod": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "etod": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "aobt": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "atod": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "stoa": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "etoa": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "atoa": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "aibt": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter querysets to only used records for Select2 autocomplete
        from masterdata.models import Airline, Airport, AircraftType, Gate, Stand, CheckInCounter, BaggageCarousel

        # Get cached IDs (avoids repeated slow queries)
        ids = get_cached_used_ids()

        # Set querysets for Select2 widgets - they'll load via AJAX but this filters what's available
        self.fields["airline"].queryset = Airline.objects.filter(id__in=ids["airline_ids"])
        self.fields["aircraft_type"].queryset = AircraftType.objects.filter(id__in=ids["aircraft_ids"])
        self.fields["origin"].queryset = Airport.objects.filter(id__in=ids["airport_ids"])
        self.fields["destination"].queryset = Airport.objects.filter(id__in=ids["airport_ids"])

        # Resources - small sets, regular dropdowns are fine
        self.fields["gate"].queryset = Gate.objects.filter(is_active=True)
        self.fields["stand"].queryset = Stand.objects.filter(is_active=True)
        self.fields["checkin_counters"].queryset = CheckInCounter.objects.filter(is_active=True)
        self.fields["carousel"].queryset = BaggageCarousel.objects.filter(is_active=True)
