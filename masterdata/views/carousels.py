from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from ..models import BaggageCarousel
from ..forms import BaggageCarouselForm


@login_required
def carousel_list(request):
    """Display list of all active baggage carousels"""
    carousels = BaggageCarousel.objects.filter(is_active=True).select_related("terminal").order_by("code")
    return render(request, "masterdata/carousel_list.html", {"carousels": carousels})


@login_required
@require_http_methods(["GET", "POST"])
def add_carousel(request):
    """Handle GET (render form) and POST (create baggage carousel)"""
    if request.method == "POST":
        form = BaggageCarouselForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = BaggageCarouselForm()

    return render(
        request,
        "masterdata/partials/carousel_form.html",
        {"form": form, "title": "Add Baggage Carousel", "action_url": "masterdata:add_carousel"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_carousel(request, pk):
    """Handle GET (render form with instance) and POST (update baggage carousel)"""
    carousel = get_object_or_404(BaggageCarousel, pk=pk)

    if request.method == "POST":
        form = BaggageCarouselForm(request.POST, instance=carousel)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = BaggageCarouselForm(instance=carousel)

    return render(
        request,
        "masterdata/partials/carousel_form.html",
        {
            "form": form,
            "title": "Edit Baggage Carousel",
            "action_url": "masterdata:edit_carousel",
            "pk": pk,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_carousel(request, pk):
    """Soft delete a baggage carousel by setting is_active=False"""
    carousel = get_object_or_404(BaggageCarousel, pk=pk)
    carousel.is_active = False
    carousel.save()

    response = HttpResponse(status=204)
    response["HX-Trigger"] = "refreshTable"
    return response
