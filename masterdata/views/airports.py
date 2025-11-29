from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q

from ..models import Airport
from ..forms import AirportForm


@login_required
def airport_list(request):
    """Display list of all active airports with pagination and search"""
    search_query = request.GET.get("search", "")

    airports = Airport.objects.filter(is_active=True)

    # Apply search filter if provided
    if search_query:
        airports = airports.filter(
            Q(iata_code__icontains=search_query)
            | Q(icao_code__icontains=search_query)
            | Q(name__icontains=search_query)
            | Q(city__icontains=search_query)
            | Q(country__icontains=search_query)
        )

    airports = airports.order_by("iata_code")

    # Pagination - 50 items per page
    paginator = Paginator(airports, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "masterdata/airport_list.html", {"page_obj": page_obj, "search_query": search_query, "total_count": airports.count()})


@login_required
@require_http_methods(["GET", "POST"])
def add_airport(request):
    """Handle GET (render form) and POST (create airport)"""
    if request.method == "POST":
        form = AirportForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Airport '{form.cleaned_data['iata_code']}' created successfully.")
            return redirect("masterdata:airport_list")
    else:
        form = AirportForm()

    return render(
        request,
        "masterdata/airport_form.html",
        {"form": form, "title": "Add Airport", "action": "Add"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_airport(request, pk):
    """Handle GET (render form with instance) and POST (update airport)"""
    airport = get_object_or_404(Airport, pk=pk)

    if request.method == "POST":
        form = AirportForm(request.POST, instance=airport)
        if form.is_valid():
            form.save()
            messages.success(request, f"Airport '{airport.iata_code}' updated successfully.")
            return redirect("masterdata:airport_list")
    else:
        form = AirportForm(instance=airport)

    return render(
        request,
        "masterdata/airport_form.html",
        {
            "form": form,
            "title": "Edit Airport",
            "action": "Update",
            "airport": airport,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_airport(request, pk):
    """Soft delete an airport by setting is_active=False"""
    airport = get_object_or_404(Airport, pk=pk)
    airport_code = airport.iata_code
    airport.is_active = False
    airport.save()

    messages.success(request, f"Airport '{airport_code}' deleted successfully.")
    return redirect("masterdata:airport_list")
