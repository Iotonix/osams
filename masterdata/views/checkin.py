from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from ..models import CheckInCounter
from ..forms import CheckInCounterForm


@login_required
def checkin_list(request):
    """Display list of all active check-in counters with search"""
    search_query = request.GET.get("search", "")

    counters = CheckInCounter.objects.filter(is_active=True).select_related("terminal")

    # Apply search filter if provided
    if search_query:
        counters = counters.filter(Q(code__icontains=search_query) | Q(terminal__code__icontains=search_query) | Q(counter_group__icontains=search_query))

    counters = counters.order_by("code")

    return render(request, "masterdata/checkin_list.html", {"counters": counters, "search_query": search_query})


@login_required
@require_http_methods(["GET", "POST"])
def add_checkin(request):
    """Handle GET (render form) and POST (create check-in counter)"""
    if request.method == "POST":
        form = CheckInCounterForm(request.POST)
        if form.is_valid():
            counter = form.save()
            messages.success(request, f"Check-in Counter '{counter.code}' created successfully.")
            return redirect("masterdata:checkin_list")
    else:
        form = CheckInCounterForm()

    return render(
        request,
        "masterdata/checkin_form.html",
        {"form": form, "title": "Add Check-in Counter", "action": "Add"},
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
            messages.success(request, f"Check-in Counter '{counter.code}' updated successfully.")
            return redirect("masterdata:checkin_list")
    else:
        form = CheckInCounterForm(instance=counter)

    return render(
        request,
        "masterdata/checkin_form.html",
        {
            "form": form,
            "title": "Edit Check-in Counter",
            "action": "Update",
            "counter": counter,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_checkin(request, pk):
    """Soft delete a check-in counter by setting is_active=False"""
    counter = get_object_or_404(CheckInCounter, pk=pk)
    counter_code = counter.code
    counter.is_active = False
    counter.save()

    messages.success(request, f"Check-in Counter '{counter_code}' deleted successfully.")
    return redirect("masterdata:checkin_list")
