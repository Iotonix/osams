"""
Seed command to populate airport infrastructure for a medium-sized airport.
This represents a typical airport with 3 terminals (T1 International, T2 International, Domestic).
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from masterdata.models import AircraftType, BaggageCarousel, CheckInCounter, Gate, Stand, Terminal


class Command(BaseCommand):
    help = "Seeds airport infrastructure data (terminals, gates, stands, counters, carousels)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting airport infrastructure seed..."))

        with transaction.atomic():
            # Clear existing data
            Terminal.objects.all().delete()
            Gate.objects.all().delete()
            Stand.objects.all().delete()
            CheckInCounter.objects.all().delete()
            BaggageCarousel.objects.all().delete()

            # Create Terminals
            t1 = Terminal.objects.create(
                code="T1",
                name="Terminal 1 - International",
                description="Main international terminal with wide-body capability",
            )
            t2 = Terminal.objects.create(
                code="T2",
                name="Terminal 2 - International",
                description="Secondary international terminal for regional flights",
            )
            t_dom = Terminal.objects.create(code="DOM", name="Domestic Terminal", description="Dedicated domestic operations terminal")

            self.stdout.write(self.style.SUCCESS(f"✓ Created {Terminal.objects.count()} terminals"))

            # Get aircraft types for gate restrictions
            narrowbody = list(AircraftType.objects.filter(size_category="NB", is_active=True)[:10])
            widebody = list(AircraftType.objects.filter(size_category="WB", is_active=True)[:5])
            regional = list(AircraftType.objects.filter(size_category="RJ", is_active=True)[:5])

            # T1 GATES (A gates - 16 gates for international wide-body and narrow-body)
            gates_created = 0
            for i in range(1, 17):
                gate = Gate.objects.create(
                    code=f"A{i}",
                    terminal=t1,
                    gate_type="CONTACT" if i <= 12 else "BOTH",  # First 12 are pure contact
                    max_wingspan_meters=79.8 if i <= 6 else 60.3,  # A1-A6 can handle A380
                    is_active=True,
                    is_available=True,
                    notes=f"{'Wide-body capable' if i <= 6 else 'Standard contact gate'}",
                )
                # A1-A6 accept wide-body, A7-A16 narrow-body
                if i <= 6 and widebody:
                    gate.allowed_aircraft_types.set(widebody + narrowbody)
                elif narrowbody:
                    gate.allowed_aircraft_types.set(narrowbody)
                gates_created += 1

            # T2 GATES (B gates - 12 gates for regional and narrow-body international)
            for i in range(1, 13):
                gate = Gate.objects.create(
                    code=f"B{i}",
                    terminal=t2,
                    gate_type="CONTACT" if i <= 8 else "REMOTE",  # B9-B12 remote
                    max_wingspan_meters=36.0,  # Code C aircraft max
                    is_active=True,
                    is_available=True,
                    notes="Regional and narrow-body operations",
                )
                if narrowbody:
                    gate.allowed_aircraft_types.set(narrowbody[:8] if regional else narrowbody)
                gates_created += 1

            # DOMESTIC GATES (C gates - 10 gates for domestic flights)
            for i in range(1, 11):
                gate = Gate.objects.create(
                    code=f"C{i}",
                    terminal=t_dom,
                    gate_type="CONTACT" if i <= 6 else "REMOTE",
                    max_wingspan_meters=36.0,
                    is_active=True,
                    is_available=True,
                    notes="Domestic operations only",
                )
                if narrowbody or regional:
                    gate.allowed_aircraft_types.set((narrowbody[:5] + regional) if regional else narrowbody[:8])
                gates_created += 1

            self.stdout.write(self.style.SUCCESS(f"✓ Created {gates_created} gates"))

            # STANDS (Remote parking positions)
            stands_data = [
                # Wide-body remote stands
                {"code": "R1", "size_code": "F", "max_wingspan": 79.8, "pushback": True, "notes": "A380 capable"},
                {"code": "R2", "size_code": "F", "max_wingspan": 79.8, "pushback": True, "notes": "A380 capable"},
                {"code": "R3", "size_code": "E", "max_wingspan": 64.8, "pushback": True, "notes": "B777/A350 position"},
                {"code": "R4", "size_code": "E", "max_wingspan": 64.8, "pushback": True, "notes": "B777/A350 position"},
                {"code": "R5", "size_code": "D", "max_wingspan": 51.8, "pushback": True, "notes": "B767/A330 position"},
                {"code": "R6", "size_code": "D", "max_wingspan": 51.8, "pushback": True, "notes": "B767/A330 position"},
                # Narrow-body remote stands
                {"code": "R10", "size_code": "C", "max_wingspan": 35.8, "pushback": True, "notes": "A320/B737 family"},
                {"code": "R11", "size_code": "C", "max_wingspan": 35.8, "pushback": True, "notes": "A320/B737 family"},
                {"code": "R12", "size_code": "C", "max_wingspan": 35.8, "pushback": True, "notes": "A320/B737 family"},
                {"code": "R13", "size_code": "C", "max_wingspan": 35.8, "pushback": True, "notes": "A320/B737 family"},
                {"code": "R14", "size_code": "C", "max_wingspan": 35.8, "pushback": True, "notes": "A320/B737 family"},
                {"code": "R15", "size_code": "C", "max_wingspan": 35.8, "pushback": True, "notes": "A320/B737 family"},
                # Regional aircraft stands
                {"code": "R20", "size_code": "B", "max_wingspan": 23.0, "pushback": False, "notes": "Regional jets, self-maneuver"},
                {"code": "R21", "size_code": "B", "max_wingspan": 23.0, "pushback": False, "notes": "Regional jets, self-maneuver"},
                {"code": "R22", "size_code": "B", "max_wingspan": 23.0, "pushback": False, "notes": "Regional jets, self-maneuver"},
                {"code": "R23", "size_code": "B", "max_wingspan": 23.0, "pushback": False, "notes": "Regional jets, self-maneuver"},
                # Cargo/maintenance stands
                {"code": "M1", "size_code": "E", "max_wingspan": 64.8, "pushback": True, "notes": "Maintenance apron"},
                {"code": "M2", "size_code": "D", "max_wingspan": 51.8, "pushback": True, "notes": "Maintenance apron"},
                {"code": "CARGO1", "size_code": "E", "max_wingspan": 64.8, "pushback": True, "notes": "Cargo operations"},
                {"code": "CARGO2", "size_code": "D", "max_wingspan": 51.8, "pushback": True, "notes": "Cargo operations"},
            ]

            for stand_data in stands_data:
                Stand.objects.create(
                    code=stand_data["code"],
                    size_code=stand_data["size_code"],
                    max_wingspan_meters=stand_data["max_wingspan"],
                    has_pushback=stand_data["pushback"],
                    notes=stand_data["notes"],
                    is_active=True,
                    is_available=True,
                )

            self.stdout.write(self.style.SUCCESS(f"✓ Created {Stand.objects.count()} stands"))

            # CHECK-IN COUNTERS
            counters_created = 0

            # T1 Check-in (International - 80 counters in 8 rows)
            for row in range(1, 9):  # Rows A-H
                row_letter = chr(64 + row)  # A=65, B=66, etc.
                for counter in range(1, 11):  # 10 counters per row
                    CheckInCounter.objects.create(
                        code=f"T1-{row_letter}{counter:02d}",
                        terminal=t1,
                        counter_group=f"Row {row_letter}",
                        is_active=True,
                        is_available=True,
                        notes="International check-in",
                    )
                    counters_created += 1

            # T2 Check-in (Regional International - 40 counters in 4 rows)
            for row in range(1, 5):  # Rows A-D
                row_letter = chr(64 + row)
                for counter in range(1, 11):
                    CheckInCounter.objects.create(
                        code=f"T2-{row_letter}{counter:02d}",
                        terminal=t2,
                        counter_group=f"Row {row_letter}",
                        is_active=True,
                        is_available=True,
                        notes="Regional international check-in",
                    )
                    counters_created += 1

            # Domestic Check-in (30 counters in 3 rows)
            for row in range(1, 4):  # Rows A-C
                row_letter = chr(64 + row)
                for counter in range(1, 11):
                    CheckInCounter.objects.create(
                        code=f"DOM-{row_letter}{counter:02d}",
                        terminal=t_dom,
                        counter_group=f"Row {row_letter}",
                        is_active=True,
                        is_available=True,
                        notes="Domestic check-in",
                    )
                    counters_created += 1

            self.stdout.write(self.style.SUCCESS(f"✓ Created {counters_created} check-in counters"))

            # BAGGAGE CAROUSELS
            carousels_created = 0

            # T1 Baggage Carousels (8 carousels for international arrivals)
            for i in range(1, 9):
                BaggageCarousel.objects.create(
                    code=f"T1-C{i}",
                    terminal=t1,
                    is_active=True,
                    is_available=True,
                    notes="International arrivals baggage claim",
                )
                carousels_created += 1

            # T2 Baggage Carousels (4 carousels for regional arrivals)
            for i in range(1, 5):
                BaggageCarousel.objects.create(
                    code=f"T2-C{i}",
                    terminal=t2,
                    is_active=True,
                    is_available=True,
                    notes="Regional international baggage claim",
                )
                carousels_created += 1

            # Domestic Baggage Carousels (5 carousels)
            for i in range(1, 6):
                BaggageCarousel.objects.create(
                    code=f"DOM-C{i}",
                    terminal=t_dom,
                    is_active=True,
                    is_available=True,
                    notes="Domestic baggage claim",
                )
                carousels_created += 1

            self.stdout.write(self.style.SUCCESS(f"✓ Created {carousels_created} baggage carousels"))

            # Summary
            self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
            self.stdout.write(self.style.SUCCESS("AIRPORT INFRASTRUCTURE SEED COMPLETE"))
            self.stdout.write(self.style.SUCCESS("=" * 60))
            self.stdout.write(f"Terminals: {Terminal.objects.count()}")
            self.stdout.write(f"Gates: {Gate.objects.count()}")
            self.stdout.write(f"Stands: {Stand.objects.count()}")
            self.stdout.write(f"Check-in Counters: {CheckInCounter.objects.count()}")
            self.stdout.write(f"Baggage Carousels: {BaggageCarousel.objects.count()}")
            self.stdout.write(self.style.SUCCESS("=" * 60))
            self.stdout.write(
                self.style.WARNING(
                    "\nThis represents a medium-sized international airport with:\n"
                    "  • T1: 16 gates (6 wide-body capable), 80 check-in counters, 8 carousels\n"
                    "  • T2: 12 gates (regional/narrow-body), 40 check-in counters, 4 carousels\n"
                    "  • DOM: 10 gates (domestic), 30 check-in counters, 5 carousels\n"
                    "  • 20 remote stands (wide-body, narrow-body, regional, cargo/maint)\n"
                )
            )
