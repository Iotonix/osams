from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from ..models import Terminal
from ..forms import TerminalForm


@login_required
def terminal_list(request):
    """Display list of all active terminals with search"""
    search_query = request.GET.get("search", "")

    terminals = Terminal.objects.filter(is_active=True)

    # Apply search filter if provided
    if search_query:
        terminals = terminals.filter(Q(code__icontains=search_query) | Q(name__icontains=search_query))

    terminals = terminals.order_by("code")

    return render(request, "masterdata/terminal_list.html", {"terminals": terminals, "search_query": search_query})


@login_required
@require_http_methods(["GET", "POST"])
def add_terminal(request):
    """Handle GET (render form) and POST (create terminal)"""
    if request.method == "POST":
        form = TerminalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Terminal '{form.cleaned_data['code']}' created successfully.")
            return redirect("masterdata:terminal_list")
    else:
        form = TerminalForm()

    return render(
        request,
        "masterdata/terminal_form.html",
        {"form": form, "title": "Add Terminal", "action": "Add"},
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
            messages.success(request, f"Terminal '{terminal.code}' updated successfully.")
            return redirect("masterdata:terminal_list")
    else:
        form = TerminalForm(instance=terminal)

    return render(
        request,
        "masterdata/terminal_form.html",
        {
            "form": form,
            "title": "Edit Terminal",
            "action": "Update",
            "terminal": terminal,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_terminal(request, pk):
    """Soft delete a terminal by setting is_active=False"""
    terminal = get_object_or_404(Terminal, pk=pk)
    terminal_code = terminal.code
    terminal.is_active = False
    terminal.save()

    messages.success(request, f"Terminal '{terminal_code}' deleted successfully.")
    return redirect("masterdata:terminal_list")
