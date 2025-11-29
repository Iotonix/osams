from django import forms
from .models import SeasonalFlight


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


class SeasonalFlightForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SeasonalFlight
        fields = [
            "airline",
            "flight_number",
            "origin",
            "destination",
            "aircraft_type",
            "service_type",
            "stod",
            "stoa",
            "start_date",
            "end_date",
            "days_of_operation",
            "is_active",
        ]
        widgets = {
            "stod": forms.TimeInput(attrs={"type": "time"}),
            "stoa": forms.TimeInput(attrs={"type": "time"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }
