from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from ..models import Route
from ..forms import RouteForm


@login_required
def route_list(request):
    """Display list of all active routes with search"""
    search_query = request.GET.get("search", "")

    routes = Route.objects.filter(is_active=True).select_related("airline", "origin", "destination")

    # Apply search filter if provided
    if search_query:
        routes = routes.filter(
            Q(airline__iata_code__icontains=search_query)
            | Q(airline__name__icontains=search_query)
            | Q(origin__iata_code__icontains=search_query)
            | Q(origin__city__icontains=search_query)
            | Q(destination__iata_code__icontains=search_query)
            | Q(destination__city__icontains=search_query)
        )

    routes = routes.order_by("airline__iata_code", "origin__iata_code", "destination__iata_code")

    return render(request, "masterdata/route_list.html", {"routes": routes, "search_query": search_query})


@login_required
@require_http_methods(["GET", "POST"])
def add_route(request):
    """Handle GET (render form) and POST (create route)"""
    if request.method == "POST":
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save()
            messages.success(request, f"Route '{route}' created successfully.")
            return redirect("masterdata:route_list")
    else:
        form = RouteForm()

    return render(
        request,
        "masterdata/route_form.html",
        {"form": form, "title": "Add Route", "action": "Add"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_route(request, pk):
    """Handle GET (render form with instance) and POST (update route)"""
    route = get_object_or_404(Route, pk=pk)

    if request.method == "POST":
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, f"Route '{route}' updated successfully.")
            return redirect("masterdata:route_list")
    else:
        form = RouteForm(instance=route)

    return render(
        request,
        "masterdata/route_form.html",
        {
            "form": form,
            "title": "Edit Route",
            "action": "Update",
            "route": route,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_route(request, pk):
    """Soft delete a route by setting is_active=False"""
    route = get_object_or_404(Route, pk=pk)
    route_str = str(route)
    route.is_active = False
    route.save()

    messages.success(request, f"Route '{route_str}' deleted successfully.")
    return redirect("masterdata:route_list")
