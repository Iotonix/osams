"""
Management command to suggest and optionally apply gate allocations for seasonal flights.

This command analyzes existing seasonal flights and suggests compatible gates based on:
1. Aircraft type compatibility
2. Wingspan restrictions
3. Historical usage patterns from daily flights
4. Terminal preferences
"""

from collections import Counter
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone

from flight_ops.models import DailyFlight
from masterdata.models import Gate, Stand, BaggageCarousel
from schedules.models import SeasonalFlight


class Command(BaseCommand):
    help = "Suggest and optionally apply gate/stand allocations for seasonal flights"

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply the suggestions automatically (default: just show suggestions)",
        )
        parser.add_argument(
            "--airline",
            type=str,
            help="Filter by airline IATA code (e.g., TG, BA)",
        )
        parser.add_argument(
            "--flight-number",
            type=str,
            help="Filter by specific flight number",
        )
        parser.add_argument(
            "--unassigned-only",
            action="store_true",
            help="Only process flights without preferred resources",
        )
        parser.add_argument(
            "--use-history",
            action="store_true",
            help="Use historical daily flight data to suggest most commonly used resources",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        airline_filter = options["airline"]
        flight_number_filter = options["flight_number"]
        unassigned_only = options["unassigned_only"]
        use_history = options["use_history"]

        self.stdout.write(self.style.WARNING("\n🎯 Gate Allocation Suggestion Tool\n"))
        self.stdout.write("=" * 70)

        # Build queryset
        queryset = SeasonalFlight.objects.filter(is_active=True).select_related(
            "airline", "aircraft_type", "origin", "destination"
        )

        if airline_filter:
            queryset = queryset.filter(airline__iata_code=airline_filter.upper())

        if flight_number_filter:
            queryset = queryset.filter(flight_number=flight_number_filter)

        if unassigned_only:
            queryset = queryset.filter(
                Q(preferred_gate__isnull=True) & Q(preferred_stand__isnull=True)
            )

        total_flights = queryset.count()
        if total_flights == 0:
            self.stdout.write(self.style.ERROR("\n✗ No seasonal flights found matching criteria."))
            return

        self.stdout.write(f"\n📋 Found {total_flights} seasonal flights to process\n")
        if apply_changes:
            self.stdout.write(self.style.WARNING("⚠️  APPLY MODE: Changes will be saved to database\n"))
        else:
            self.stdout.write(self.style.SUCCESS("👁️  PREVIEW MODE: No changes will be saved (use --apply to save)\n"))

        updated_count = 0
        skipped_count = 0
        error_count = 0

        for flight in queryset:
            try:
                suggestion = self._generate_suggestion(flight, use_history)

                if suggestion["skip"]:
                    skipped_count += 1
                    if not apply_changes:
                        self._print_flight_status(flight, suggestion, "SKIP")
                    continue

                # Show suggestion
                if not apply_changes:
                    self._print_flight_status(flight, suggestion, "SUGGEST")

                # Apply if requested
                if apply_changes:
                    changes_made = False

                    if suggestion["gate"] and not flight.preferred_gate:
                        flight.preferred_gate = suggestion["gate"]
                        changes_made = True

                    if suggestion["stand"] and not flight.preferred_stand:
                        flight.preferred_stand = suggestion["stand"]
                        changes_made = True

                    if suggestion["carousel"] and not flight.preferred_carousel:
                        flight.preferred_carousel = suggestion["carousel"]
                        changes_made = True

                    if changes_made:
                        flight.save()
                        updated_count += 1
                        self._print_flight_status(flight, suggestion, "APPLIED")
                    else:
                        skipped_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"   ✗ Error processing {flight.airline.iata_code}{flight.flight_number}: {str(e)}"
                    )
                )

        # Summary
        self.stdout.write("\n" + "=" * 70)
        if apply_changes:
            self.stdout.write(self.style.SUCCESS(f"✓ Updated {updated_count} seasonal flights"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✓ Generated {updated_count} suggestions"))

        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f"⊘ Skipped {skipped_count} flights (already assigned or no compatible resources)"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"✗ Errors: {error_count}"))

        self.stdout.write("=" * 70 + "\n")

        if not apply_changes and updated_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    "\n💡 To apply these suggestions, run the command again with --apply flag\n"
                )
            )

    def _generate_suggestion(self, flight, use_history):
        """Generate gate/stand/carousel suggestions for a seasonal flight."""
        result = {
            "gate": None,
            "stand": None,
            "carousel": None,
            "skip": False,
            "reason": None,
            "confidence": "unknown",
        }

        # Skip if already has all resources assigned
        if flight.preferred_gate and flight.preferred_stand and flight.preferred_carousel:
            result["skip"] = True
            result["reason"] = "Already fully assigned"
            return result

        # Check historical usage if requested
        if use_history:
            historical = self._get_historical_usage(flight)
            if historical["gate"]:
                result["gate"] = historical["gate"]
                result["confidence"] = "historical"
            if historical["stand"]:
                result["stand"] = historical["stand"]
            if historical["carousel"]:
                result["carousel"] = historical["carousel"]

        # If no historical data or not requested, use compatibility-based suggestion
        if not result["gate"] and not flight.preferred_gate:
            result["gate"] = self._find_compatible_gate(flight)
            if result["gate"] and result["confidence"] == "unknown":
                result["confidence"] = "compatibility"

        if not result["stand"] and not flight.preferred_stand:
            result["stand"] = self._find_compatible_stand(flight)

        if not result["carousel"] and not flight.preferred_carousel:
            result["carousel"] = self._find_available_carousel()

        # If nothing found, mark as skip
        if not result["gate"] and not result["stand"]:
            result["skip"] = True
            result["reason"] = "No compatible resources found"

        return result

    def _get_historical_usage(self, flight):
        """Analyze historical daily flights to find most commonly used resources."""
        # Look back 90 days
        cutoff_date = timezone.now().date() - timedelta(days=90)

        daily_flights = DailyFlight.objects.filter(
            airline=flight.airline,
            flight_number=flight.flight_number,
            date_of_operation__gte=cutoff_date,
        ).select_related("gate", "stand", "carousel")

        if not daily_flights.exists():
            return {"gate": None, "stand": None, "carousel": None}

        # Count most common resources
        gates = [df.gate for df in daily_flights if df.gate]
        stands = [df.stand for df in daily_flights if df.stand]
        carousels = [df.carousel for df in daily_flights if df.carousel]

        result = {
            "gate": Counter(gates).most_common(1)[0][0] if gates else None,
            "stand": Counter(stands).most_common(1)[0][0] if stands else None,
            "carousel": Counter(carousels).most_common(1)[0][0] if carousels else None,
        }

        # Validate historical gate is still compatible
        if result["gate"]:
            if not self._validate_gate_compatibility(flight, result["gate"]):
                result["gate"] = None

        return result

    def _find_compatible_gate(self, flight):
        """Find a compatible gate based on aircraft type and wingspan."""
        gates = Gate.objects.filter(is_active=True)

        # Filter by allowed aircraft types (if gate has restrictions)
        compatible_gates = []
        for gate in gates:
            if self._validate_gate_compatibility(flight, gate):
                compatible_gates.append(gate)

        if not compatible_gates:
            return None

        # Prefer gates with fewer restrictions (more flexible)
        # Sort by: 1) No aircraft restrictions, 2) Higher wingspan capacity
        compatible_gates.sort(
            key=lambda g: (
                0 if not g.allowed_aircraft_types.exists() else 1,
                -(g.max_wingspan_meters or 999),
            )
        )

        return compatible_gates[0] if compatible_gates else None

    def _validate_gate_compatibility(self, flight, gate):
        """Check if a gate is compatible with the flight's aircraft."""
        aircraft = flight.aircraft_type

        # Check allowed aircraft types
        if gate.allowed_aircraft_types.exists():
            if aircraft not in gate.allowed_aircraft_types.all():
                return False

        # Check wingspan
        if gate.max_wingspan_meters:
            if aircraft.wingspan_meters > gate.max_wingspan_meters:
                return False

        return True

    def _find_compatible_stand(self, flight):
        """Find a compatible stand based on aircraft size."""
        aircraft = flight.aircraft_type

        stands = Stand.objects.filter(
            is_active=True,
            max_wingspan_meters__gte=aircraft.wingspan_meters,
        ).order_by("max_wingspan_meters")

        return stands.first() if stands.exists() else None

    def _find_available_carousel(self):
        """Find any available carousel (simple round-robin suggestion)."""
        carousels = BaggageCarousel.objects.filter(is_active=True).order_by("code")
        return carousels.first() if carousels.exists() else None

    def _print_flight_status(self, flight, suggestion, status):
        """Print formatted flight status with suggestion details."""
        status_colors = {
            "SUGGEST": self.style.SUCCESS,
            "APPLIED": self.style.SUCCESS,
            "SKIP": self.style.WARNING,
        }

        color = status_colors.get(status, self.style.WARNING)

        flight_id = f"{flight.airline.iata_code}{flight.flight_number}"
        aircraft = flight.aircraft_type.icao_code
        route = f"{flight.origin.iata_code}->{flight.destination.iata_code}"

        self.stdout.write(
            color(f"\n[{status}] {flight_id:8} | {aircraft:4} | {route:10}")
        )

        if suggestion["skip"]:
            self.stdout.write(f"   Reason: {suggestion['reason']}")
        else:
            if suggestion["gate"]:
                self.stdout.write(f"   Gate: {suggestion['gate'].code}")
            if suggestion["stand"]:
                self.stdout.write(f"   Stand: {suggestion['stand'].code}")
            if suggestion["carousel"]:
                self.stdout.write(f"   Carousel: {suggestion['carousel'].code}")
            if suggestion["confidence"]:
                self.stdout.write(f"   Confidence: {suggestion['confidence']}")
