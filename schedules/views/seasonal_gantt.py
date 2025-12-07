from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from masterdata.models import Airline
from ..models import SeasonalFlight


@login_required
def seasonal_gantt_view(request):
    """
    Render the GANTT chart view for seasonal flight schedules.
    Shows timeline visualization with nested groups for each flight.
    """
    # Get all airlines for filter dropdown
    airlines = Airline.objects.filter(is_active=True).order_by("iata_code")
    
    context = {
        "airlines": airlines,
        "today": datetime.now().strftime("%Y-%m-%d"),
    }
    
    return render(request, "schedules/seasonal_gantt.html", context)


@login_required
def seasonal_gantt_data(request):
    """
    API endpoint that returns JSON data for Vis.js Timeline.
    Shows a typical day view based on day of week filter.
    
    Returns:
        {
            "groups": [...],  # Flight groups (one per flight number)
            "items": [...]    # Resource occupation items (gate, carousel, etc.)
        }
    """
    # Get filter parameters
    airline_filter = request.GET.get("airline", "")
    search_query = request.GET.get("search", "")
    day_of_week = request.GET.get("day_of_week", "1")  # 1=Monday, 7=Sunday
    
    # Base queryset: active seasonal flights only
    flights = SeasonalFlight.objects.filter(is_active=True).select_related(
        "airline",
        "origin",
        "destination",
        "aircraft_type",
        "preferred_gate",
        "preferred_gate__terminal",
        "preferred_stand",
        "preferred_carousel",
        "preferred_carousel__terminal",
    )
    
    # Apply filters
    if airline_filter and airline_filter != "--":
        flights = flights.filter(airline__iata_code=airline_filter)
    
    if search_query:
        flights = flights.filter(
            Q(airline__iata_code__icontains=search_query)
            | Q(airline__name__icontains=search_query)
            | Q(flight_number__icontains=search_query)
            | Q(origin__iata_code__icontains=search_query)
            | Q(destination__iata_code__icontains=search_query)
        )
    
    # Filter by day of week (1=Monday, 7=Sunday)
    # days_of_operation field contains digits: "1234567" = all days, "135" = Mon/Wed/Fri
    if day_of_week:
        flights = flights.filter(days_of_operation__contains=day_of_week)
    
    flights = flights.order_by("airline__iata_code", "flight_number")
    
    # Build groups based on RESOURCES (gates, stands, carousels)
    # This way we'll have ~50 groups instead of 1800+
    groups = []
    items = []
    item_id = 1
    
    # Collect all unique resources from the flights
    resources_seen = set()
    gate_groups = {}
    carousel_groups = {}
    
    for flight in flights:
        flight_code = f"{flight.airline.iata_code}{flight.flight_number}"
        
        # Use a reference date for visualization (today for timeline display)
        reference_date = datetime.now().date()
        
        # Determine if this is arrival or departure
        is_arrival_at_sin = flight.destination.iata_code == "SIN"
        is_departure_from_sin = flight.origin.iata_code == "SIN"
        
        if is_arrival_at_sin:
            ground_start = datetime.combine(reference_date, flight.stoa)
            ground_end = ground_start + timedelta(hours=2)
        elif is_departure_from_sin:
            ground_end = datetime.combine(reference_date, flight.stod)
            ground_start = ground_end - timedelta(hours=2)
        else:
            ground_start = datetime.combine(reference_date, flight.stod)
            ground_end = ground_start + timedelta(hours=1)
        
        # ITEM 1: Gate/Stand Occupation
        if flight.preferred_gate:
            resource_id = f"gate_{flight.preferred_gate.id}"
            if resource_id not in resources_seen:
                resources_seen.add(resource_id)
                gate_groups[resource_id] = f"{flight.preferred_gate.code} (T{flight.preferred_gate.terminal.code})"
            
            gate_label = f"{flight_code}"
            items.append({
                "id": item_id,
                "group": resource_id,
                "start": ground_start.isoformat(),
                "end": ground_end.isoformat(),
                "content": gate_label,
                "title": f"{flight_code} - {flight.preferred_gate.code}",
                "className": "item-gate",
                "type": "range",
            })
            item_id += 1
        elif flight.preferred_stand:
            resource_id = f"stand_{flight.preferred_stand.id}"
            if resource_id not in resources_seen:
                resources_seen.add(resource_id)
                gate_groups[resource_id] = f"{flight.preferred_stand.code} (Stand)"
            
            stand_label = f"{flight_code}"
            items.append({
                "id": item_id,
                "group": resource_id,
                "start": ground_start.isoformat(),
                "end": ground_end.isoformat(),
                "content": stand_label,
                "title": f"{flight_code} - {flight.preferred_stand.code}",
                "className": "item-gate",
                "type": "range",
            })
            item_id += 1
        
        # ITEM 2: Carousel Occupation (starts 30 min after ground start)
        if flight.preferred_carousel:
            carousel_start = ground_start + timedelta(minutes=30)
            carousel_end = carousel_start + timedelta(minutes=45)
            
            resource_id = f"carousel_{flight.preferred_carousel.id}"
            if resource_id not in resources_seen:
                resources_seen.add(resource_id)
                carousel_groups[resource_id] = f"{flight.preferred_carousel.code} (T{flight.preferred_carousel.terminal.code})"
            
            carousel_label = f"{flight_code}"
            items.append({
                "id": item_id,
                "group": resource_id,
                "start": carousel_start.isoformat(),
                "end": carousel_end.isoformat(),
                "content": carousel_label,
                "title": f"{flight_code} Baggage - {flight.preferred_carousel.code}",
                "className": "item-carousel",
                "type": "range",
            })
            item_id += 1
    
    # Now create groups from the collected resources
    # Gates/Stands section
    if gate_groups:
        groups.append({
            "id": "gates_header",
            "content": "<strong>GATES & STANDS</strong>",
            "className": "group-header",
            "nestedGroups": list(gate_groups.keys()),
            "showNested": True,  # Start expanded so items are visible
        })
        for resource_id, label in sorted(gate_groups.items(), key=lambda x: x[1]):
            groups.append({
                "id": resource_id,
                "content": label,
                "className": "group-resource",
                "treeLevel": 2,
            })
    
    # Carousels section
    if carousel_groups:
        groups.append({
            "id": "carousels_header",
            "content": "<strong>BAGGAGE CAROUSELS</strong>",
            "className": "group-header",
            "nestedGroups": list(carousel_groups.keys()),
            "showNested": True,  # Start expanded so items are visible
        })
        for resource_id, label in sorted(carousel_groups.items(), key=lambda x: x[1]):
            groups.append({
                "id": resource_id,
                "content": label,
                "className": "group-resource",
                "treeLevel": 2,
            })
    
    return JsonResponse({
        "groups": groups,
        "items": items,
        "count": flights.count(),  # Number of flights
    })
