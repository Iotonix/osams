from django import forms
from .models import (
    Airline,
    Airport,
    AircraftType,
    Terminal,
    Gate,
    Stand,
    CheckInCounter,
    BaggageCarousel,
    GroundHandler,
    Route,
    Runway,
)


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


class AirlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Airline
        fields = [
            "iata_code",
            "icao_code",
            "name",
            "country",
            "contact_email",
            "contact_phone",
            "is_active",
        ]


class AirportForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Airport
        fields = [
            "iata_code",
            "icao_code",
            "name",
            "city",
            "country",
            "latitude",
            "longitude",
            "is_active",
        ]


class AircraftTypeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AircraftType
        fields = [
            "icao_code",
            "iata_code",
            "manufacturer",
            "model",
            "wake_turbulence",
            "size_category",
            "wingspan_meters",
            "length_meters",
            "max_takeoff_weight_kg",
            "typical_capacity",
            "is_active",
        ]


class TerminalForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Terminal
        fields = [
            "code",
            "name",
            "description",
            "is_active",
        ]


class GateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Gate
        fields = [
            "code",
            "terminal",
            "gate_type",
            "max_wingspan_meters",
            "is_active",
            "is_available",
            "notes",
        ]


class StandForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Stand
        fields = [
            "code",
            "size_code",
            "max_wingspan_meters",
            "has_pushback",
            "is_active",
            "is_available",
            "notes",
        ]


class CheckInCounterForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CheckInCounter
        fields = [
            "code",
            "terminal",
            "counter_group",
            "is_active",
            "is_available",
            "notes",
        ]


class BaggageCarouselForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = BaggageCarousel
        fields = [
            "code",
            "terminal",
            "is_active",
            "is_available",
            "notes",
        ]


class GroundHandlerForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GroundHandler
        fields = [
            "code",
            "name",
            "contact_email",
            "contact_phone",
            "provides_passenger",
            "provides_ramp",
            "provides_cargo",
            "is_active",
        ]


class RouteForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Route
        fields = [
            "airline",
            "origin",
            "destination",
            "codeshare",
            "stops",
            "equipment",
            "is_active",
        ]


class RunwayForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Runway
        fields = [
            "name",
            "length_meters",
            "width_meters",
            "surface",
            "is_active",
        ]
