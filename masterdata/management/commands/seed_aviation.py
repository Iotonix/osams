# masterdata/management/commands/seed_aviation.py

import csv
import io

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from masterdata.models import AircraftType, Airline, Airport, Route
from os_ams import settings


class Command(BaseCommand):
    help = "Seeds the database with OpenFlights Airline and Aircraft data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Aviation Data Seed...")

        # # 1. SEED AIRLINES
        # self.seed_airlines()

        # # 2. SEED AIRCRAFT
        # self.seed_aircraft()

        # # 3. SEED AIRPORTS (New)
        # self.seed_airports()

        # 4. SEED ROUTES
        self.seed_routes()

        self.stdout.write(self.style.SUCCESS("Data seeding completed successfully!"))

    def seed_airlines(self):
        url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat"
        self.stdout.write(f"Fetching Airlines from {url}...")

        response = requests.get(url)
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(io.StringIO(content), delimiter=",")

        count = 0
        with transaction.atomic():
            for row in csv_reader:
                # OpenFlights Format:
                # ID, Name, Alias, IATA, ICAO, Callsign, Country, Active
                try:
                    name = row[1]
                    iata = row[3]
                    icao = row[4]
                    country = row[6]
                    active_status = row[7]

                    # Filter: Only active airlines with valid codes
                    if active_status == "Y" and len(iata) == 2 and len(icao) == 3:
                        Airline.objects.update_or_create(
                            icao_code=icao, defaults={"iata_code": iata, "name": name, "country": country, "is_active": True}
                        )
                        count += 1
                except IndexError:
                    continue
                except Exception as e:
                    # Skip duplicates or bad regex matches silently
                    continue

        self.stdout.write(self.style.SUCCESS(f"Imported/Updated {count} Airlines."))

    def seed_aircraft(self):
        # Using OpenFlights aircraft database
        url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/planes.dat"
        self.stdout.write(f"Fetching Aircraft Types from {url}...")

        response = requests.get(url)
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(io.StringIO(content), delimiter=",")

        count = 0
        with transaction.atomic():
            for row in csv_reader:
                # OpenFlights planes.dat Format:
                # Name, IATA code, ICAO code
                try:
                    full_name = row[0]
                    iata = row[1] if len(row) > 1 else ""
                    icao = row[2] if len(row) > 2 else ""

                    if len(icao) >= 3 and len(icao) <= 4:
                        # Split Name into Manufacturer and Model (Heuristic)
                        parts = full_name.split(" ", 1)
                        manufacturer = parts[0] if len(parts) > 1 else "Generic"
                        model = parts[1] if len(parts) > 1 else parts[0]

                        # NOTE: Open data DOES NOT have wingspan/weight.
                        # We set defaults to allow the save. You must update these
                        # for your specific airport operations manually.
                        AircraftType.objects.update_or_create(
                            icao_code=icao,
                            defaults={
                                "iata_code": iata[:3] if iata else None,
                                "manufacturer": manufacturer[:100],
                                "model": model[:100],
                                "wake_turbulence": "M",  # Default Medium
                                "size_category": "NB",  # Default Narrow Body
                                "wingspan_meters": 35.00,  # Placeholder - typical narrow body
                                "length_meters": 37.00,  # Placeholder
                                "max_takeoff_weight_kg": 75000,  # Placeholder
                                "typical_capacity": 150,  # Placeholder
                            },
                        )
                        count += 1
                except Exception as e:
                    continue

        self.stdout.write(self.style.SUCCESS(f"Imported/Updated {count} Aircraft Types."))

    def seed_airports(self):
        url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
        self.stdout.write(f"Fetching Airports from {url}...")

        response = requests.get(url)
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(io.StringIO(content), delimiter=",")

        count = 0
        with transaction.atomic():
            for row in csv_reader:
                # OpenFlights airports.dat Format:
                # 0: ID, 1: Name, 2: City, 3: Country, 4: IATA, 5: ICAO, 6: Lat, 7: Lon ...
                try:
                    name = row[1]
                    city = row[2]
                    country = row[3]
                    iata = row[4]
                    icao = row[5]
                    lat = row[6]
                    lon = row[7]

                    # Filter: Require both IATA (3 chars) and ICAO (4 chars)
                    # Many small airports in the dataset use "\N" or empty strings for missing codes
                    if len(iata) == 3 and len(icao) == 4 and iata != "\\N" and icao != "\\N":
                        Airport.objects.update_or_create(
                            icao_code=icao,
                            defaults={
                                "iata_code": iata,
                                "name": name,
                                "city": city,
                                "country": country,
                                "latitude": lat,
                                "longitude": lon,
                                "is_active": True,
                            },
                        )
                        count += 1
                except IndexError:
                    continue
                except Exception as e:
                    continue

        self.stdout.write(self.style.SUCCESS(f"Imported/Updated {count} Airports."))

    def seed_routes(self):
        url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
        self.stdout.write(f"Fetching Routes from {url}...")

        response = requests.get(url)
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(io.StringIO(content), delimiter=",")

        # Cache lookups to speed up processing (Critical for 60k+ routes)
        # We map IATA/ICAO codes to database IDs
        airlines_map = {a.iata_code: a.id for a in Airline.objects.all() if a.iata_code}
        # Also map ICAO for airlines just in case
        airlines_map.update({a.icao_code: a.id for a in Airline.objects.all() if a.icao_code})

        # For airports, we map both IATA and ICAO to IDs
        airports_map = {a.iata_code: a.id for a in Airport.objects.all() if a.iata_code}
        airports_map.update({a.icao_code: a.id for a in Airport.objects.all() if a.icao_code})

        routes_to_create = []
        count = 0

        self.stdout.write("Processing route data (this might take a moment)...")

        for row in csv_reader:
            # Format: 0:Airline, 1:ID, 2:Origin, 3:ID, 4:Dest, 5:ID, 6:Codeshare, 7:Stops, 8:Equip
            try:
                airline_code = row[0]
                origin_code = row[2]
                dest_code = row[4]
                codeshare = row[6] == "Y"
                stops = int(row[7]) if row[7] else 0
                equipment = row[8]

                # Fast Lookup
                airline_id = airlines_map.get(airline_code)
                origin_id = airports_map.get(origin_code)
                dest_id = airports_map.get(dest_code)

                # FILTER LOGIC:
                # Only keep routes that touch our Home Airport (either Origin OR Destination)
                is_outbound = (origin_code == settings.HOME_AIRPORT_IATA) or (origin_code == settings.HOME_AIRPORT_ICAO)
                is_inbound = (dest_code == settings.HOME_AIRPORT_IATA) or (dest_code == settings.HOME_AIRPORT_ICAO)
                if not (is_outbound or is_inbound):
                    continue  # Skip this route, it's irrelevant to us

                if airline_id and origin_id and dest_id:
                    # We use bulk_create for routes because checking get_or_create
                    # for 67,000 routes is too slow one-by-one.
                    routes_to_create.append(
                        Route(airline_id=airline_id, origin_id=origin_id, destination_id=dest_id, codeshare=codeshare, stops=stops, equipment=equipment)
                    )
                    count += 1
            except (IndexError, ValueError):
                continue

        # Bulk Create to save time
        # ignore_conflicts=True handles duplicates defined in unique_together
        with transaction.atomic():
            Route.objects.bulk_create(routes_to_create, batch_size=1000, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f"Imported {count} Routes."))
