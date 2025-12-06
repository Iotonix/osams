from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from schedules.models import SeasonalFlight
from masterdata.models import Gate, Stand, BaggageCarousel


class Command(BaseCommand):
    help = "Auto-allocate gates, stands, and carousels to seasonal flights based on compatibility rules"

    def add_arguments(self, parser):
        parser.add_argument(
            "--preview",
            action="store_true",
            help="Preview suggestions without applying changes",
        )
        parser.add_argument(
            "--airline",
            type=str,
            help="Filter by airline IATA code (e.g., TG, BA)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing assignments",
        )

    def handle(self, *args, **options):
        preview = options["preview"]
        airline_filter = options.get("airline")
        force = options["force"]

        self.stdout.write(self.style.WARNING("\n🎯 Seasonal Resource Auto-Allocation"))
        self.stdout.write(f"Mode: {'PREVIEW' if preview else 'APPLY'}")
        if force:
            self.stdout.write("Force: Will overwrite existing assignments")
        self.stdout.write("")

        # Build queryset
        flights_qs = SeasonalFlight.objects.filter(is_active=True).select_related(
            "airline", "aircraft_type", "origin", "destination", "preferred_gate", "preferred_stand", "preferred_carousel"
        )

        if airline_filter:
            flights_qs = flights_qs.filter(airline__iata_code=airline_filter)

        # Filter only flights without assignments (unless force=True)
        if not force:
            flights_qs = flights_qs.filter(
                Q(preferred_gate__isnull=True) | Q(preferred_stand__isnull=True) | Q(preferred_carousel__isnull=True)
            )

        total_flights = flights_qs.count()

        if total_flights == 0:
            self.stdout.write(self.style.WARNING("✓ No seasonal flights need resource allocation"))
            return

        self.stdout.write(f"📋 Processing {total_flights} seasonal flights\n")

        # Get available resources (active and available)
        all_gates = Gate.objects.filter(is_active=True, is_available=True).select_related("terminal").prefetch_related("allowed_aircraft_types")
        
        # Separate gates by terminal type (Domestic vs International)
        domestic_gates = list(all_gates.filter(terminal__code='DOM'))
        international_gates = list(all_gates.exclude(terminal__code='DOM'))
        
        # Separate stands by type - exclude CARGO stands for regular allocation
        all_stands = Stand.objects.filter(is_active=True, is_available=True)
        stands = list(all_stands.exclude(code__istartswith='CARGO'))  # Regular stands
        cargo_stands = list(all_stands.filter(code__istartswith='CARGO'))  # Cargo stands
        
        carousels = list(BaggageCarousel.objects.filter(is_active=True, is_available=True).select_related("terminal"))

        if not domestic_gates and not international_gates:
            self.stdout.write(self.style.ERROR("✗ No active gates available in the system"))
            return
            
        if not stands:
            self.stdout.write(self.style.WARNING("⚠ No remote stands available"))

        # Statistics
        assigned_gate = 0
        assigned_stand = 0
        assigned_carousel = 0
        skipped = 0
        errors = 0

        # Round-robin counters to distribute resources evenly (separate for domestic/international)
        domestic_gate_index = 0
        international_gate_index = 0
        stand_index = 0
        carousel_index = 0

        with transaction.atomic():
            for flight in flights_qs:
                try:
                    suggested_gate = None
                    suggested_stand = None
                    suggested_carousel = None
                    changes = []

                    # === GATE ALLOCATION ===
                    if force or not flight.preferred_gate:
                        # Determine if flight is domestic (both origin and destination in Thailand)
                        is_domestic = (
                            flight.origin and flight.destination and
                            flight.origin.country == 'Thailand' and 
                            flight.destination.country == 'Thailand'
                        )
                        
                        # Select appropriate gate pool
                        if is_domestic:
                            gate_pool = domestic_gates
                            gate_idx = domestic_gate_index
                        else:
                            gate_pool = international_gates
                            gate_idx = international_gate_index
                        
                        suggested_gate = self._find_compatible_gate(flight, gate_pool, gate_idx)
                        if suggested_gate:
                            # Update the appropriate index
                            if is_domestic:
                                domestic_gate_index = (gate_pool.index(suggested_gate) + 1) % len(gate_pool)
                            else:
                                international_gate_index = (gate_pool.index(suggested_gate) + 1) % len(gate_pool)
                                
                            if not preview:
                                flight.preferred_gate = suggested_gate
                                # Automatically assign the stand linked to this gate
                                if suggested_gate.stand:
                                    flight.preferred_stand = suggested_gate.stand
                            assigned_gate += 1
                            stand_info = f"/{suggested_gate.stand.code}" if suggested_gate.stand else ""
                            terminal_info = "(DOM)" if is_domestic else "(INTL)"
                            changes.append(f"Gate:{suggested_gate.code}{stand_info}{terminal_info}")

                    # === STANDALONE STAND ALLOCATION ===
                    # Only for flights without a gate assignment (cargo, overflow)
                    if (force or not flight.preferred_stand) and not suggested_gate and not flight.preferred_gate:
                        # Cargo flights get cargo stands
                        if flight.service_type == 'F':
                            suggested_stand = self._find_compatible_stand(flight, cargo_stands, stand_index)
                            if suggested_stand:
                                stand_index = (cargo_stands.index(suggested_stand) + 1) % len(cargo_stands)
                                if not preview:
                                    flight.preferred_stand = suggested_stand
                                assigned_stand += 1
                                changes.append(f"Stand:{suggested_stand.code}(Cargo)")
                        # Passenger overflow: assign remote stand
                        else:
                            suggested_stand = self._find_compatible_stand(flight, stands, stand_index)
                            if suggested_stand:
                                stand_index = (stands.index(suggested_stand) + 1) % len(stands)
                                if not preview:
                                    flight.preferred_stand = suggested_stand
                                assigned_stand += 1
                                changes.append(f"Stand:{suggested_stand.code}(Remote)")

                    # === CAROUSEL ALLOCATION (for arrivals only) ===
                    if force or not flight.preferred_carousel:
                        # Only allocate carousel for arriving flights
                        if flight.destination.iata_code == "BKK":  # Adjust to your home airport
                            suggested_carousel = self._find_compatible_carousel(flight, carousels, carousel_index)
                            if suggested_carousel:
                                carousel_index = (carousels.index(suggested_carousel) + 1) % len(carousels)
                                if not preview:
                                    flight.preferred_carousel = suggested_carousel
                                assigned_carousel += 1
                                changes.append(f"Carousel:{suggested_carousel.code}")

                    # Save changes
                    if not preview and changes:
                        flight.save()

                    # Single line output per flight
                    if changes:
                        change_str = ", ".join(changes)
                        self.stdout.write(f"  {flight.airline.iata_code}{flight.flight_number:>4} ({flight.aircraft_type.icao_code}) → {change_str}")

                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ {flight.airline.iata_code}{flight.flight_number}: {str(e)}"))

        # Summary
        self.stdout.write("\n" + "=" * 60)
        if preview:
            self.stdout.write(self.style.SUCCESS(f"📊 PREVIEW Results:"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✓ Resource Allocation Complete"))

        self.stdout.write(f"   Gates assigned: {assigned_gate}")
        self.stdout.write(f"   Stands assigned: {assigned_stand}")
        self.stdout.write(f"   Carousels assigned: {assigned_carousel}")

        if errors > 0:
            self.stdout.write(self.style.ERROR(f"   Errors: {errors}"))

        self.stdout.write("=" * 60 + "\n")

        if preview:
            self.stdout.write(self.style.WARNING("ℹ️  Run without --preview to apply changes"))

    def _find_compatible_gate(self, flight, gates, start_index):
        """Find a compatible gate using round-robin distribution"""
        aircraft_type = flight.aircraft_type

        # Try gates starting from start_index for even distribution
        for i in range(len(gates)):
            gate = gates[(start_index + i) % len(gates)]

            # Check if gate has specific aircraft restrictions
            if gate.allowed_aircraft_types.exists():
                if aircraft_type not in gate.allowed_aircraft_types.all():
                    continue

            # Check wingspan constraint
            if gate.max_wingspan_meters:
                if aircraft_type.wingspan_meters > gate.max_wingspan_meters:
                    continue

            # Found a compatible gate
            return gate

        return None

    def _find_compatible_stand(self, flight, stands, start_index):
        """Find a compatible stand using round-robin distribution"""
        aircraft_type = flight.aircraft_type

        # Try stands starting from start_index for even distribution
        for i in range(len(stands)):
            stand = stands[(start_index + i) % len(stands)]

            # Check wingspan constraint
            if stand.max_wingspan_meters:
                if aircraft_type.wingspan_meters > stand.max_wingspan_meters:
                    continue

            # Found a compatible stand
            return stand

        return None

    def _find_compatible_carousel(self, flight, carousels, start_index):
        """Find a compatible carousel using round-robin distribution"""
        # Simple round-robin for carousels (no complex compatibility rules)
        if carousels:
            return carousels[start_index % len(carousels)]
        return None
