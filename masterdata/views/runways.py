from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from ..models import Runway
from ..forms import RunwayForm


@login_required
def runway_list(request):
    """Display list of all active runways with search"""
    search_query = request.GET.get("search", "")

    runways = Runway.objects.filter(is_active=True)

    # Apply search filter if provided
    if search_query:
        runways = runways.filter(Q(name__icontains=search_query))

    runways = runways.order_by("name")

    return render(request, "masterdata/runway_list.html", {"runways": runways, "search_query": search_query})


@login_required
@require_http_methods(["GET", "POST"])
def add_runway(request):
    """Handle GET (render form) and POST (create runway)"""
    if request.method == "POST":
        form = RunwayForm(request.POST)
        if form.is_valid():
            runway = form.save()
            messages.success(request, f"Runway '{runway.name}' created successfully.")
            return redirect("masterdata:runway_list")
    else:
        form = RunwayForm()

    return render(
        request,
        "masterdata/runway_form.html",
        {"form": form, "title": "Add Runway", "action": "Add"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_runway(request, pk):
    """Handle GET (render form with instance) and POST (update runway)"""
    runway = get_object_or_404(Runway, pk=pk)

    if request.method == "POST":
        form = RunwayForm(request.POST, instance=runway)
        if form.is_valid():
            form.save()
            messages.success(request, f"Runway '{runway.name}' updated successfully.")
            return redirect("masterdata:runway_list")
    else:
        form = RunwayForm(instance=runway)

    return render(
        request,
        "masterdata/runway_form.html",
        {
            "form": form,
            "title": "Edit Runway",
            "action": "Update",
            "runway": runway,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_runway(request, pk):
    """Soft delete a runway by setting is_active=False"""
    runway = get_object_or_404(Runway, pk=pk)
    runway_name = runway.name
    runway.is_active = False
    runway.save()

    messages.success(request, f"Runway '{runway_name}' deleted successfully.")
    return redirect("masterdata:runway_list")
