from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from ..models import CheckInCounter
from ..forms import CheckInCounterForm


@login_required
def checkin_list(request):
    """Display list of all active check-in counters"""
    counters = CheckInCounter.objects.filter(is_active=True).select_related("terminal").order_by("code")
    return render(request, "masterdata/checkin_list.html", {"counters": counters})


@login_required
@require_http_methods(["GET", "POST"])
def add_checkin(request):
    """Handle GET (render form) and POST (create check-in counter)"""
    if request.method == "POST":
        form = CheckInCounterForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = CheckInCounterForm()

    return render(
        request,
        "masterdata/partials/checkin_form.html",
        {"form": form, "title": "Add Check-in Counter", "action_url": "masterdata:add_checkin"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_checkin(request, pk):
    """Handle GET (render form with instance) and POST (update check-in counter)"""
    counter = get_object_or_404(CheckInCounter, pk=pk)

    if request.method == "POST":
        form = CheckInCounterForm(request.POST, instance=counter)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = CheckInCounterForm(instance=counter)

    return render(
        request,
        "masterdata/partials/checkin_form.html",
        {
            "form": form,
            "title": "Edit Check-in Counter",
            "action_url": "masterdata:edit_checkin",
            "pk": pk,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_checkin(request, pk):
    """Soft delete a check-in counter by setting is_active=False"""
    counter = get_object_or_404(CheckInCounter, pk=pk)
    counter.is_active = False
    counter.save()

    response = HttpResponse(status=204)
    response["HX-Trigger"] = "refreshTable"
    return response
