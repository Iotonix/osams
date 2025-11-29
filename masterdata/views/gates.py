from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from ..models import Gate
from ..forms import GateForm


@login_required
def gate_list(request):
    """Display list of all active gates"""
    gates = Gate.objects.filter(is_active=True).select_related("terminal").order_by("code")
    return render(request, "masterdata/gate_list.html", {"gates": gates})


@login_required
@require_http_methods(["GET", "POST"])
def add_gate(request):
    """Handle GET (render form) and POST (create gate)"""
    if request.method == "POST":
        form = GateForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = GateForm()

    return render(
        request,
        "masterdata/partials/gate_form.html",
        {"form": form, "title": "Add Gate", "action_url": "masterdata:add_gate"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_gate(request, pk):
    """Handle GET (render form with instance) and POST (update gate)"""
    gate = get_object_or_404(Gate, pk=pk)

    if request.method == "POST":
        form = GateForm(request.POST, instance=gate)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = GateForm(instance=gate)

    return render(
        request,
        "masterdata/partials/gate_form.html",
        {
            "form": form,
            "title": "Edit Gate",
            "action_url": "masterdata:edit_gate",
            "pk": pk,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_gate(request, pk):
    """Soft delete a gate by setting is_active=False"""
    gate = get_object_or_404(Gate, pk=pk)
    gate.is_active = False
    gate.save()

    response = HttpResponse(status=204)
    response["HX-Trigger"] = "refreshTable"
    return response
