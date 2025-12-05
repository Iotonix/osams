import random
from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from masterdata.models import Terminal, Gate, Stand, CheckInCounter, BaggageCarousel, Airline, AircraftType
from flight_ops.models import DailyFlight


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
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Flight statistics
    flights_today = DailyFlight.objects.filter(date_of_operation=today).count()
    flights_yesterday = DailyFlight.objects.filter(date_of_operation=yesterday).count()
    
    # Calculate percentage change
    if flights_yesterday > 0:
        flights_change_pct = round(((flights_today - flights_yesterday) / flights_yesterday) * 100, 1)
    else:
        flights_change_pct = 0
    
    # Gate statistics
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
        "flights_today": flights_today,
        "flights_change_pct": flights_change_pct,
        "flights_change_direction": "up" if flights_change_pct >= 0 else "down",
    }
    return render(request, "index.html", context)
