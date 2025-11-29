from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from ..forms import DailyFlightForm
from ..models import DailyFlight


@login_required
def daily_flight_list(request):
    """Display list of all daily flights with search"""
    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    daily_flights = DailyFlight.objects.select_related(
        "airline",
        "origin",
        "destination",
        "aircraft_type",
        "gate",
        "stand",
        "carousel",
        "schedule",
    ).prefetch_related("checkin_counters")

    # Apply search filter if provided
    if search_query:
        daily_flights = daily_flights.filter(
            Q(airline__iata_code__icontains=search_query)
            | Q(airline__name__icontains=search_query)
            | Q(flight_number__icontains=search_query)
            | Q(flight_id__icontains=search_query)
            | Q(registration__icontains=search_query)
        )

    # Apply status filter if provided
    if status_filter:
        daily_flights = daily_flights.filter(status=status_filter)

    daily_flights = daily_flights.order_by("-date_of_operation", "stod", "airline", "flight_number")

    return render(
        request,
        "flight_ops/daily_flight_list.html",
        {
            "daily_flights": daily_flights,
            "search_query": search_query,
            "status_filter": status_filter,
            "status_choices": DailyFlight.STATUS_CHOICES,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def add_daily_flight(request):
    """Handle GET (render form) and POST (create daily flight)"""
    if request.method == "POST":
        form = DailyFlightForm(request.POST)
        if form.is_valid():
            daily_flight = form.save()
            messages.success(
                request,
                f"Daily Flight '{daily_flight.airline.iata_code}{daily_flight.flight_number}' created successfully.",
            )
            return redirect("flight_ops:daily_flight_list")
    else:
        form = DailyFlightForm()

    return render(
        request,
        "flight_ops/daily_flight_form.html",
        {"form": form, "title": "Add Daily Flight", "action": "Add"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_daily_flight(request, pk):
    """Handle GET (render form with instance) and POST (update daily flight)"""
    daily_flight = get_object_or_404(DailyFlight, pk=pk)

    if request.method == "POST":
        form = DailyFlightForm(request.POST, instance=daily_flight)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Daily Flight '{daily_flight.airline.iata_code}{daily_flight.flight_number}' updated successfully.",
            )
            return redirect("flight_ops:daily_flight_list")
    else:
        form = DailyFlightForm(instance=daily_flight)

    return render(
        request,
        "flight_ops/daily_flight_form.html",
        {
            "form": form,
            "title": "Edit Daily Flight",
            "action": "Update",
            "daily_flight": daily_flight,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_daily_flight(request, pk):
    """Hard delete a daily flight"""
    daily_flight = get_object_or_404(DailyFlight, pk=pk)
    flight_name = f"{daily_flight.airline.iata_code}{daily_flight.flight_number}"
    daily_flight.delete()

    messages.success(request, f"Daily Flight '{flight_name}' deleted successfully.")
    return redirect("flight_ops:daily_flight_list")
