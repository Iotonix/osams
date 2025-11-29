from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from ..forms import SeasonalFlightForm
from ..models import SeasonalFlight


@login_required
def seasonal_flight_list(request):
    """Display list of all active seasonal flights with search"""
    search_query = request.GET.get("search", "")

    seasonal_flights = SeasonalFlight.objects.filter(is_active=True).select_related("airline", "origin", "destination", "aircraft_type")

    # Apply search filter if provided
    if search_query:
        seasonal_flights = seasonal_flights.filter(
            Q(airline__iata_code__icontains=search_query)
            | Q(airline__name__icontains=search_query)
            | Q(flight_number__icontains=search_query)
            | Q(origin__iata_code__icontains=search_query)
            | Q(destination__iata_code__icontains=search_query)
        )

    seasonal_flights = seasonal_flights.order_by("airline", "flight_number")

    return render(
        request,
        "schedules/seasonal_flight_list.html",
        {"seasonal_flights": seasonal_flights, "search_query": search_query},
    )


@login_required
@require_http_methods(["GET", "POST"])
def add_seasonal_flight(request):
    """Handle GET (render form) and POST (create seasonal flight)"""
    if request.method == "POST":
        form = SeasonalFlightForm(request.POST)
        if form.is_valid():
            seasonal_flight = form.save()
            messages.success(
                request,
                f"Seasonal Flight '{seasonal_flight.airline.iata_code}{seasonal_flight.flight_number}' created successfully.",
            )
            return redirect("schedules:seasonal_flight_list")
    else:
        form = SeasonalFlightForm()

    return render(
        request,
        "schedules/seasonal_flight_form.html",
        {"form": form, "title": "Add Seasonal Flight", "action": "Add"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_seasonal_flight(request, pk):
    """Handle GET (render form with instance) and POST (update seasonal flight)"""
    seasonal_flight = get_object_or_404(SeasonalFlight, pk=pk)

    if request.method == "POST":
        form = SeasonalFlightForm(request.POST, instance=seasonal_flight)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Seasonal Flight '{seasonal_flight.airline.iata_code}{seasonal_flight.flight_number}' updated successfully.",
            )
            return redirect("schedules:seasonal_flight_list")
    else:
        form = SeasonalFlightForm(instance=seasonal_flight)

    return render(
        request,
        "schedules/seasonal_flight_form.html",
        {
            "form": form,
            "title": "Edit Seasonal Flight",
            "action": "Update",
            "seasonal_flight": seasonal_flight,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_seasonal_flight(request, pk):
    """Soft delete a seasonal flight by setting is_active=False"""
    seasonal_flight = get_object_or_404(SeasonalFlight, pk=pk)
    flight_name = f"{seasonal_flight.airline.iata_code}{seasonal_flight.flight_number}"
    seasonal_flight.is_active = False
    seasonal_flight.save()

    messages.success(request, f"Seasonal Flight '{flight_name}' deleted successfully.")
    return redirect("schedules:seasonal_flight_list")
