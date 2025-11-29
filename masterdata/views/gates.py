from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from ..models import Gate
from ..forms import GateForm


@login_required
def gate_list(request):
    """Display list of all active gates with search"""
    search_query = request.GET.get("search", "")

    gates = Gate.objects.filter(is_active=True).select_related("terminal")

    # Apply search filter if provided
    if search_query:
        gates = gates.filter(Q(code__icontains=search_query) | Q(terminal__code__icontains=search_query))

    gates = gates.order_by("code")

    return render(request, "masterdata/gate_list.html", {"gates": gates, "search_query": search_query})


@login_required
@require_http_methods(["GET", "POST"])
def add_gate(request):
    """Handle GET (render form) and POST (create gate)"""
    if request.method == "POST":
        form = GateForm(request.POST)
        if form.is_valid():
            gate = form.save()
            messages.success(request, f"Gate '{gate.code}' created successfully.")
            return redirect("masterdata:gate_list")
    else:
        form = GateForm()

    return render(
        request,
        "masterdata/gate_form.html",
        {"form": form, "title": "Add Gate", "action": "Add"},
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
            messages.success(request, f"Gate '{gate.code}' updated successfully.")
            return redirect("masterdata:gate_list")
    else:
        form = GateForm(instance=gate)

    return render(
        request,
        "masterdata/gate_form.html",
        {
            "form": form,
            "title": "Edit Gate",
            "action": "Update",
            "gate": gate,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_gate(request, pk):
    """Soft delete a gate by setting is_active=False"""
    gate = get_object_or_404(Gate, pk=pk)
    gate_code = gate.code
    gate.is_active = False
    gate.save()

    messages.success(request, f"Gate '{gate_code}' deleted successfully.")
    return redirect("masterdata:gate_list")
