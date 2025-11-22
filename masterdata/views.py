from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import (
    Airline, AircraftType, Terminal, Gate, Stand,
    CheckInCounter, BaggageCarousel
)


@login_required
def airline_list(request):
    airlines = Airline.objects.filter(is_active=True).order_by('iata_code')
    return render(request, 'masterdata/airline_list.html', {'airlines': airlines})


@login_required
def aircraft_list(request):
    aircraft = AircraftType.objects.filter(is_active=True).order_by('icao_code')
    return render(request, 'masterdata/aircraft_list.html', {'aircraft': aircraft})


@login_required
def terminal_list(request):
    terminals = Terminal.objects.filter(is_active=True).order_by('code')
    return render(request, 'masterdata/terminal_list.html', {'terminals': terminals})


@login_required
def gate_list(request):
    gates = Gate.objects.filter(is_active=True).select_related('terminal').order_by('code')
    return render(request, 'masterdata/gate_list.html', {'gates': gates})


@login_required
def stand_list(request):
    stands = Stand.objects.filter(is_active=True).order_by('code')
    return render(request, 'masterdata/stand_list.html', {'stands': stands})


@login_required
def checkin_list(request):
    counters = CheckInCounter.objects.filter(is_active=True).select_related('terminal').order_by('code')
    return render(request, 'masterdata/checkin_list.html', {'counters': counters})


@login_required
def carousel_list(request):
    carousels = BaggageCarousel.objects.filter(is_active=True).select_related('terminal').order_by('code')
    return render(request, 'masterdata/carousel_list.html', {'carousels': carousels})
