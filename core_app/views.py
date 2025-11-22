import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from masterdata.models import Terminal, Gate, Stand, CheckInCounter, BaggageCarousel, Airline, AircraftType


def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next") or "dashboard"
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def user_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("login")


@login_required
def dashboard(request):
    total_gates = Gate.objects.count()
    occupied_gates = random.randint(0, total_gates) if total_gates > 0 else 0
    pax_throughput_hourly = occupied_gates * 100

    context = {
        "terminal_count": Terminal.objects.count(),
        "gate_count": total_gates,
        "stand_count": Stand.objects.count(),
        "checkin_count": CheckInCounter.objects.count(),
        "carousel_count": BaggageCarousel.objects.count(),
        "airline_count": Airline.objects.count(),
        "aircraft_count": AircraftType.objects.count(),
        "occupied_gates": occupied_gates,
        "pax_throughput_hourly": pax_throughput_hourly,
    }
    return render(request, "index.html", context)
