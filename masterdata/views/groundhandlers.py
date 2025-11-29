from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from ..models import GroundHandler
from ..forms import GroundHandlerForm


@login_required
def groundhandler_list(request):
    """Display list of all active ground handlers with search"""
    search_query = request.GET.get("search", "")

    handlers = GroundHandler.objects.filter(is_active=True)

    # Apply search filter if provided
    if search_query:
        handlers = handlers.filter(Q(code__icontains=search_query) | Q(name__icontains=search_query))

    handlers = handlers.order_by("code")

    return render(request, "masterdata/groundhandler_list.html", {"handlers": handlers, "search_query": search_query})


@login_required
@require_http_methods(["GET", "POST"])
def add_groundhandler(request):
    """Handle GET (render form) and POST (create ground handler)"""
    if request.method == "POST":
        form = GroundHandlerForm(request.POST)
        if form.is_valid():
            handler = form.save()
            messages.success(request, f"Ground Handler '{handler.name}' created successfully.")
            return redirect("masterdata:groundhandler_list")
    else:
        form = GroundHandlerForm()

    return render(
        request,
        "masterdata/groundhandler_form.html",
        {"form": form, "title": "Add Ground Handler", "action": "Add"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_groundhandler(request, pk):
    """Handle GET (render form with instance) and POST (update ground handler)"""
    handler = get_object_or_404(GroundHandler, pk=pk)

    if request.method == "POST":
        form = GroundHandlerForm(request.POST, instance=handler)
        if form.is_valid():
            form.save()
            messages.success(request, f"Ground Handler '{handler.name}' updated successfully.")
            return redirect("masterdata:groundhandler_list")
    else:
        form = GroundHandlerForm(instance=handler)

    return render(
        request,
        "masterdata/groundhandler_form.html",
        {
            "form": form,
            "title": "Edit Ground Handler",
            "action": "Update",
            "handler": handler,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_groundhandler(request, pk):
    """Soft delete a ground handler by setting is_active=False"""
    handler = get_object_or_404(GroundHandler, pk=pk)
    handler_name = handler.name
    handler.is_active = False
    handler.save()

    messages.success(request, f"Ground Handler '{handler_name}' deleted successfully.")
    return redirect("masterdata:groundhandler_list")
