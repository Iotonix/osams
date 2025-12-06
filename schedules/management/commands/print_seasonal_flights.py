from django.core.management.base import BaseCommand
from schedules.models import SeasonalFlight


class Command(BaseCommand):
    help = "Print seasonal flights in a single-line format (same as web view)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--airline",
            type=str,
            help="Filter by airline IATA code (e.g., TG, 3K)",
        )
        parser.add_argument(
            "--search",
            type=str,
            help="Search by airline, flight number, or airports",
        )

    def handle(self, *args, **options):
        airline_filter = options.get("airline")
        search_query = options.get("search")

        # Build queryset
        flights = SeasonalFlight.objects.filter(is_active=True).select_related(
            "airline",
            "aircraft_type",
            "origin",
            "destination",
            "preferred_gate",
            "preferred_gate__terminal",
            "preferred_stand",
            "preferred_carousel",
        ).order_by("airline__iata_code", "flight_number")

        # Apply filters
        if airline_filter:
            flights = flights.filter(airline__iata_code=airline_filter)

        if search_query:
            from django.db.models import Q
            flights = flights.filter(
                Q(airline__iata_code__icontains=search_query)
                | Q(flight_number__icontains=search_query)
                | Q(origin__iata_code__icontains=search_query)
                | Q(destination__iata_code__icontains=search_query)
            )

        total = flights.count()
        self.stdout.write(self.style.SUCCESS(f"\n📋 Seasonal Flights ({total} flights)\n"))
        self.stdout.write("=" * 120)

        for flight in flights:
            # Flight number
            flight_code = f"{flight.airline.iata_code}{flight.flight_number}"
            
            # Route
            route = f"{flight.origin.iata_code}->{flight.destination.iata_code}"
            
            # Aircraft
            aircraft = flight.aircraft_type.icao_code
            
            # Resources
            resources = []
            if flight.preferred_gate:
                terminal_code = flight.preferred_gate.terminal.code if flight.preferred_gate.terminal else "?"
                resources.append(f"Gate:{flight.preferred_gate.code}({terminal_code})")
            if flight.preferred_stand:
                resources.append(f"Stand:{flight.preferred_stand.code}")
            if flight.preferred_carousel:
                resources.append(f"Carousel:{flight.preferred_carousel.code}")
            
            resource_str = ", ".join(resources) if resources else "Not assigned"
            
            # Times
            dep_time = flight.stod.strftime("%H:%M") if flight.stod else "N/A"
            arr_time = flight.stoa.strftime("%H:%M") if flight.stoa else "N/A"
            times = f"DEP:{dep_time} ARR:{arr_time}"
            
            # Validity
            start = flight.start_date.strftime("%d-%b-%y")
            end = flight.end_date.strftime("%d-%b-%y")
            validity = f"{start} to {end}"
            
            # Days
            days = flight.days_of_operation
            
            # Print single line
            self.stdout.write(
                f"{flight_code:8} | {route:11} | {aircraft:4} | {resource_str:45} | {times:20} | {validity:23} | {days}"
            )

        self.stdout.write("=" * 120)
        self.stdout.write(self.style.SUCCESS(f"\n✓ Total: {total} flights\n"))
