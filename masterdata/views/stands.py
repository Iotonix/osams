from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from ..models import Stand
from ..forms import StandForm


@login_required
def stand_list(request):
    """Display list of all active stands with search"""
    search_query = request.GET.get("search", "")

    stands = Stand.objects.filter(is_active=True)

    # Apply search filter if provided
    if search_query:
        stands = stands.filter(Q(code__icontains=search_query))

    stands = stands.order_by("code")

    return render(request, "masterdata/stand_list.html", {"stands": stands, "search_query": search_query})


@login_required
@require_http_methods(["GET", "POST"])
def add_stand(request):
    """Handle GET (render form) and POST (create stand)"""
    if request.method == "POST":
        form = StandForm(request.POST)
        if form.is_valid():
            stand = form.save()
            messages.success(request, f"Stand '{stand.code}' created successfully.")
            return redirect("masterdata:stand_list")
    else:
        form = StandForm()

    return render(
        request,
        "masterdata/stand_form.html",
        {"form": form, "title": "Add Stand", "action": "Add"},
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
            messages.success(request, f"Stand '{stand.code}' updated successfully.")
            return redirect("masterdata:stand_list")
    else:
        form = StandForm(instance=stand)

    return render(
        request,
        "masterdata/stand_form.html",
        {
            "form": form,
            "title": "Edit Stand",
            "action": "Update",
            "stand": stand,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_stand(request, pk):
    """Soft delete a stand by setting is_active=False"""
    stand = get_object_or_404(Stand, pk=pk)
    stand_code = stand.code
    stand.is_active = False
    stand.save()

    messages.success(request, f"Stand '{stand_code}' deleted successfully.")
    return redirect("masterdata:stand_list")
