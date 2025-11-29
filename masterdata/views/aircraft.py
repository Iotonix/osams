from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from ..models import AircraftType
from ..forms import AircraftTypeForm


@login_required
def aircraft_list(request):
    """Display list of all active aircraft types"""
    aircraft = AircraftType.objects.filter(is_active=True).order_by("icao_code")
    return render(request, "masterdata/aircraft_list.html", {"aircraft": aircraft})


@login_required
@require_http_methods(["GET", "POST"])
def add_aircraft(request):
    """Handle GET (render form) and POST (create aircraft type)"""
    if request.method == "POST":
        form = AircraftTypeForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = AircraftTypeForm()

    return render(
        request,
        "masterdata/partials/aircraft_form.html",
        {"form": form, "title": "Add Aircraft Type", "action_url": "masterdata:add_aircraft"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_aircraft(request, pk):
    """Handle GET (render form with instance) and POST (update aircraft type)"""
    aircraft = get_object_or_404(AircraftType, pk=pk)

    if request.method == "POST":
        form = AircraftTypeForm(request.POST, instance=aircraft)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = AircraftTypeForm(instance=aircraft)

    return render(
        request,
        "masterdata/partials/aircraft_form.html",
        {
            "form": form,
            "title": "Edit Aircraft Type",
            "action_url": "masterdata:edit_aircraft",
            "pk": pk,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_aircraft(request, pk):
    """Soft delete an aircraft type by setting is_active=False"""
    aircraft = get_object_or_404(AircraftType, pk=pk)
    aircraft.is_active = False
    aircraft.save()

    response = HttpResponse(status=204)
    response["HX-Trigger"] = "refreshTable"
    return response
