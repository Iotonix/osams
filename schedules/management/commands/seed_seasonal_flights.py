import random
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from masterdata.models import AircraftType, Airport, Route
from schedules.models import SeasonalFlight


class Command(BaseCommand):
    help = "Seed seasonal flight schedules from existing routes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--season",
            type=str,
            default="winter2526",
            choices=["winter2526", "summer2026"],
            help="Which season to seed (winter2526 or summer2026)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing seasonal flights before seeding",
        )
        parser.add_argument(
            "--flights-per-route",
            type=int,
            default=1,
            help="Average number of flight variations per route (1-3)",
        )

    def handle(self, *args, **options):
        season = options["season"]
        clear = options["clear"]
        flights_per_route = min(max(options["flights_per_route"], 1), 3)

        # Define season dates
        if season == "winter2526":
            start_date = datetime(2025, 10, 27).date()
            end_date = datetime(2026, 3, 28).date()
            season_name = "Winter 2025/2026"
        else:  # summer2026
            start_date = datetime(2026, 3, 29).date()
            end_date = datetime(2026, 10, 24).date()
            season_name = "Summer 2026"

        self.stdout.write(self.style.WARNING(f"\n🛫 Seeding {season_name} Seasonal Flights"))
        self.stdout.write(f"   Season: {start_date} to {end_date}\n")

        # Clear existing if requested
        if clear:
            count = SeasonalFlight.objects.filter(start_date=start_date).count()
            if count > 0:
                SeasonalFlight.objects.filter(start_date=start_date).delete()
                self.stdout.write(self.style.WARNING(f"✓ Cleared {count} existing seasonal flights\n"))

        # Get home airport
        try:
            home_airport = Airport.objects.get(iata_code=settings.HOME_AIRPORT_IATA)
        except Airport.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"✗ Home airport {settings.HOME_AIRPORT_IATA} not found!"))
            return

        # Get all active routes
        routes = Route.objects.filter(is_active=True).select_related("airline", "origin", "destination")
        total_routes = routes.count()

        if total_routes == 0:
            self.stdout.write(self.style.ERROR("✗ No active routes found!"))
            return

        self.stdout.write(f"📋 Found {total_routes} active routes")
        self.stdout.write(f"🎲 Creating ~{flights_per_route} flight(s) per route\n")

        # Get available aircraft types
        aircraft_types = list(AircraftType.objects.filter(is_active=True))
        if not aircraft_types:
            self.stdout.write(self.style.ERROR("✗ No active aircraft types found!"))
            return

        # Categorize aircraft by size
        narrow_body = [ac for ac in aircraft_types if ac.size_category in ["NB", "RJ"]]
        wide_body = [ac for ac in aircraft_types if ac.size_category == "WB"]

        if not narrow_body:
            narrow_body = aircraft_types
        if not wide_body:
            wide_body = aircraft_types

        # Frequency patterns
        frequency_patterns = [
            ("1234567", 0.40),  # Daily - 40%
            ("12345", 0.30),  # Weekdays - 30%
            ("135", 0.15),  # Mon/Wed/Fri - 15%
            ("246", 0.10),  # Tue/Thu/Sat - 10%
            ("67", 0.05),  # Weekends - 5%
        ]

        # Flight number counter per airline
        flight_numbers = {}

        created_count = 0
        skipped_count = 0

        with transaction.atomic():
            for route in routes:
                airline_key = route.airline.iata_code

                # Initialize flight number for this airline if needed
                if airline_key not in flight_numbers:
                    flight_numbers[airline_key] = 100

                # Determine if this is a hub route (from or to home airport)
                is_hub_route = route.origin.iata_code == settings.HOME_AIRPORT_IATA or route.destination.iata_code == settings.HOME_AIRPORT_IATA

                # Calculate approximate distance (rough estimate)
                if route.origin.latitude and route.destination.latitude:
                    distance = self._calculate_distance(
                        route.origin.latitude,
                        route.origin.longitude,
                        route.destination.latitude,
                        route.destination.longitude,
                    )
                else:
                    distance = 2000  # Default medium distance

                # Determine number of flights for this route
                if is_hub_route and distance > 1000:
                    num_flights = min(flights_per_route + 1, 3)  # More flights for hub routes
                else:
                    num_flights = flights_per_route

                # Create flights for this route
                for flight_idx in range(num_flights):
                    # Get flight number (even for outbound, odd for return)
                    flight_num = flight_numbers[airline_key]
                    flight_numbers[airline_key] += 1

                    # Select frequency based on route type and flight index
                    if flight_idx == 0:  # First flight - more frequent
                        if is_hub_route:
                            frequency = "1234567"  # Daily for hub routes
                        else:
                            frequency = self._select_frequency(frequency_patterns)
                    else:  # Additional flights - less frequent
                        frequency = random.choice(["12345", "135", "246", "67"])

                    # Select aircraft based on distance
                    if distance < 1500:
                        aircraft = random.choice(narrow_body)
                    elif distance < 4000:
                        aircraft = random.choice(narrow_body + wide_body)
                    else:
                        aircraft = random.choice(wide_body)

                    # Generate departure time (spread throughout day)
                    if flight_idx == 0:
                        dep_hour = random.choice([6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21])
                    else:
                        dep_hour = random.choice([7, 9, 12, 15, 18, 22])

                    dep_minute = random.choice([0, 15, 30, 45])
                    stod = time(dep_hour, dep_minute)

                    # Calculate flight duration based on distance
                    duration_hours = self._calculate_duration(distance)
                    arrival_time = datetime.combine(datetime.today(), stod) + timedelta(hours=duration_hours)
                    stoa = arrival_time.time()

                    # Service type
                    service_type = "J"  # Passenger

                    try:
                        SeasonalFlight.objects.create(
                            airline=route.airline,
                            flight_number=str(flight_num),
                            origin=route.origin,
                            destination=route.destination,
                            aircraft_type=aircraft,
                            service_type=service_type,
                            stod=stod,
                            stoa=stoa,
                            start_date=start_date,
                            end_date=end_date,
                            days_of_operation=frequency,
                            is_active=True,
                        )
                        created_count += 1

                        if created_count % 100 == 0:
                            self.stdout.write(f"   Created {created_count} flights...")

                    except Exception as e:
                        skipped_count += 1
                        if skipped_count <= 5:  # Only show first few errors
                            self.stdout.write(self.style.WARNING(f"   ⚠ Skipped flight {airline_key}{flight_num}: {str(e)}"))

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"✓ Created {created_count} seasonal flights"))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f"⚠ Skipped {skipped_count} flights (duplicates or errors)"))
        self.stdout.write("=" * 60 + "\n")

        # Statistics
        self.stdout.write("\n📊 Statistics:")
        for freq, _ in frequency_patterns:
            count = SeasonalFlight.objects.filter(start_date=start_date, days_of_operation=freq).count()
            freq_label = self._frequency_label(freq)
            self.stdout.write(f"   {freq_label}: {count} flights")

        self.stdout.write(f"\n✈️  Total seasonal flights: {SeasonalFlight.objects.filter(start_date=start_date).count()}")

    def _select_frequency(self, patterns):
        """Select frequency based on weighted probabilities"""
        rand = random.random()
        cumulative = 0
        for freq, prob in patterns:
            cumulative += prob
            if rand <= cumulative:
                return freq
        return patterns[0][0]  # Default to daily

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate approximate distance in km using Haversine formula"""
        from math import asin, cos, radians, sin, sqrt

        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6371 * c  # Earth radius in km
        return km

    def _calculate_duration(self, distance_km):
        """Calculate flight duration in hours based on distance"""
        # Average speed ~800 km/h, plus taxi/climb/descent time
        if distance_km < 500:
            return 1.0
        elif distance_km < 1500:
            return distance_km / 750 + 0.5
        elif distance_km < 4000:
            return distance_km / 800 + 0.75
        else:
            return distance_km / 850 + 1.0

    def _frequency_label(self, freq):
        """Convert frequency code to readable label"""
        labels = {
            "1234567": "Daily (1234567)",
            "12345": "Weekdays (12345)",
            "135": "Mon/Wed/Fri (135)",
            "246": "Tue/Thu/Sat (246)",
            "67": "Weekends (67)",
        }
        return labels.get(freq, f"Custom ({freq})")
