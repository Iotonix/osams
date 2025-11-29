from django import forms
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
