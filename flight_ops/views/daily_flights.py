import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from ..forms import DailyFlightForm
from ..models import DailyFlight

logger = logging.getLogger(__name__)


@login_required
def daily_flight_list(request):
    """Display list of all daily flights with search"""
    from datetime import date, timedelta

    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")
    date_filter = request.GET.get("date", "")

    # Parse date filter (default to today)
    if date_filter:
        try:
            from datetime import datetime

            selected_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

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

    # Filter by selected date
    daily_flights = daily_flights.filter(date_of_operation=selected_date)

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

    daily_flights = daily_flights.order_by("stod", "airline", "flight_number")

    # Calculate prev/next dates
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)

    logger.info(f"Daily flight list view loaded: {daily_flights.count()} flights for {selected_date}")

    return render(
        request,
        "flight_ops/daily_flight_list.html",
        {
            "daily_flights": daily_flights,
            "search_query": search_query,
            "status_filter": status_filter,
            "selected_date": selected_date,
            "prev_date": prev_date,
            "next_date": next_date,
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
            logger.info(f"Daily flight created: {daily_flight.airline.iata_code}{daily_flight.flight_number} by {request.user}")
            return redirect("flight_ops:daily_flight_list")
    else:
        form = DailyFlightForm()

    logger.info(f"Add daily flight form loaded for user {request.user}")

    return render(
        request,
        "flight_ops/daily_flight_form.html",
        {"form": form, "title": "Add Daily Flight", "action": "Add"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_daily_flight(request, pk):
    """Handle GET (render form with instance) and POST (update daily flight)"""
    daily_flight = get_object_or_404(
        DailyFlight.objects.select_related("airline", "origin", "destination", "aircraft_type", "gate", "stand", "carousel", "schedule").prefetch_related(
            "checkin_counters"
        ),
        pk=pk,
    )

    if request.method == "POST":
        form = DailyFlightForm(request.POST, instance=daily_flight)
        if form.is_valid():
            # Mark as manually modified when edited through UI
            daily_flight = form.save(commit=False)
            daily_flight.is_manually_modified = True
            daily_flight.save()
            form.save_m2m()  # Save many-to-many relationships

            messages.success(
                request,
                f"Daily Flight '{daily_flight.airline.iata_code}{daily_flight.flight_number}' updated successfully.",
            )
            logger.info(f"Daily flight updated: {daily_flight.airline.iata_code}{daily_flight.flight_number} (pk={pk}) by {request.user}")
            return redirect("flight_ops:daily_flight_list")
    else:
        form = DailyFlightForm(instance=daily_flight)

    logger.info(f"Edit daily flight form loaded: {daily_flight.airline.iata_code}{daily_flight.flight_number} (pk={pk}) for user {request.user}")

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
