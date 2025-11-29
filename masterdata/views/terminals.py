from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from ..models import Terminal
from ..forms import TerminalForm


@login_required
def terminal_list(request):
    """Display list of all active terminals"""
    terminals = Terminal.objects.filter(is_active=True).order_by("code")
    return render(request, "masterdata/terminal_list.html", {"terminals": terminals})


@login_required
@require_http_methods(["GET", "POST"])
def add_terminal(request):
    """Handle GET (render form) and POST (create terminal)"""
    if request.method == "POST":
        form = TerminalForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = TerminalForm()

    return render(
        request,
        "masterdata/partials/terminal_form.html",
        {"form": form, "title": "Add Terminal", "action_url": "masterdata:add_terminal"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_terminal(request, pk):
    """Handle GET (render form with instance) and POST (update terminal)"""
    terminal = get_object_or_404(Terminal, pk=pk)

    if request.method == "POST":
        form = TerminalForm(request.POST, instance=terminal)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "refreshTable"
            return response
    else:
        form = TerminalForm(instance=terminal)

    return render(
        request,
        "masterdata/partials/terminal_form.html",
        {
            "form": form,
            "title": "Edit Terminal",
            "action_url": "masterdata:edit_terminal",
            "pk": pk,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_terminal(request, pk):
    """Soft delete a terminal by setting is_active=False"""
    terminal = get_object_or_404(Terminal, pk=pk)
    terminal.is_active = False
    terminal.save()

    response = HttpResponse(status=204)
    response["HX-Trigger"] = "refreshTable"
    return response
