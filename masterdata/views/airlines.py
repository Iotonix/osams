from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from ..models import Airline
from ..forms import AirlineForm


@login_required
def airline_list(request):
    """Display list of all active airlines"""
    airlines = Airline.objects.filter(is_active=True).order_by("iata_code")
    return render(request, "masterdata/airline_list.html", {"airlines": airlines})


@login_required
@require_http_methods(["GET", "POST"])
def add_airline(request):
    """Handle GET (render form) and POST (create airline)"""
    if request.method == "POST":
        form = AirlineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Airline '{form.cleaned_data['name']}' created successfully.")
            return redirect("masterdata:airline_list")
    else:
        form = AirlineForm()

    return render(
        request,
        "masterdata/airline_form.html",
        {"form": form, "title": "Add Airline", "action": "Add"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_airline(request, pk):
    """Handle GET (render form with instance) and POST (update airline)"""
    airline = get_object_or_404(Airline, pk=pk)

    if request.method == "POST":
        form = AirlineForm(request.POST, instance=airline)
        if form.is_valid():
            form.save()
            messages.success(request, f"Airline '{airline.name}' updated successfully.")
            return redirect("masterdata:airline_list")
    else:
        form = AirlineForm(instance=airline)

    return render(
        request,
        "masterdata/airline_form.html",
        {
            "form": form,
            "title": "Edit Airline",
            "action": "Update",
            "airline": airline,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_airline(request, pk):
    """Soft delete an airline by setting is_active=False"""
    airline = get_object_or_404(Airline, pk=pk)
    airline_name = airline.name
    airline.is_active = False
    airline.save()

    messages.success(request, f"Airline '{airline_name}' deleted successfully.")
    return redirect("masterdata:airline_list")
