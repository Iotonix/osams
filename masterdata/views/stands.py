from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from ..models import Stand
from ..forms import StandForm


@login_required
def stand_list(request):
    """Display list of all active stands"""
    stands = Stand.objects.filter(is_active=True).order_by("code")
    return render(request, "masterdata/stand_list.html", {"stands": stands})


@login_required
@require_http_methods(["GET", "POST"])
def add_stand(request):
    """Handle GET (render form) and POST (create stand)"""
    if request.method == "POST":
        form = StandForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = StandForm()

    return render(
        request,
        "masterdata/partials/stand_form.html",
        {"form": form, "title": "Add Stand", "action_url": "masterdata:add_stand"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_stand(request, pk):
    """Handle GET (render form with instance) and POST (update stand)"""
    stand = get_object_or_404(Stand, pk=pk)

    if request.method == "POST":
        form = StandForm(request.POST, instance=stand)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = StandForm(instance=stand)

    return render(
        request,
        "masterdata/partials/stand_form.html",
        {
            "form": form,
            "title": "Edit Stand",
            "action_url": "masterdata:edit_stand",
            "pk": pk,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_stand(request, pk):
    """Soft delete a stand by setting is_active=False"""
    stand = get_object_or_404(Stand, pk=pk)
    stand.is_active = False
    stand.save()

    response = HttpResponse(status=204)
    response["HX-Trigger"] = "refreshTable"
    return response
