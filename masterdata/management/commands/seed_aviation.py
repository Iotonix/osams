# masterdata/management/commands/seed_aviation.py

import csv
import io

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from masterdata.models import AircraftType, Airline, Airport


class Command(BaseCommand):
    help = "Seeds the database with OpenFlights Airline and Aircraft data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Aviation Data Seed...")

        # 1. SEED AIRLINES
        self.seed_airlines()

        # 2. SEED AIRCRAFT
        self.seed_aircraft()

        # 3. SEED AIRPORTS (New)
        self.seed_airports()

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
