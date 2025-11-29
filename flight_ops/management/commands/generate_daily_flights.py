from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from flight_ops.models import DailyFlight
from schedules.models import SeasonalFlight


class Command(BaseCommand):
    help = "Generate daily flight operations from seasonal schedules (Rolling Window Strategy)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Number of days to generate ahead (default: 90)",
        )
        parser.add_argument(
            "--start-date",
            type=str,
            default="today",
            help="Start date (YYYY-MM-DD or 'today')",
        )
        parser.add_argument(
            "--incremental",
            action="store_true",
            help="Only generate new flights (skip existing dates)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually creating",
        )

    def handle(self, *args, **options):
        days = options["days"]
        start_date_str = options["start_date"]
        incremental = options["incremental"]
        dry_run = options["dry_run"]

        # Parse start date
        if start_date_str == "today":
            start_date = timezone.now().date()
        else:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                self.stdout.write(self.style.ERROR(f"✗ Invalid date format: {start_date_str}. Use YYYY-MM-DD"))
                return

        end_date = start_date + timedelta(days=days - 1)

        self.stdout.write(self.style.WARNING(f"\n✈️  Generating Daily Flights - Rolling Window Strategy"))
        self.stdout.write(f"   Period: {start_date} to {end_date} ({days} days)")
        self.stdout.write(f"   Mode: {'INCREMENTAL' if incremental else 'FULL'}")
        if dry_run:
            self.stdout.write(self.style.WARNING("   DRY RUN - No changes will be made\n"))
        else:
            self.stdout.write("")

        # Get active seasonal flights
        seasonal_flights = SeasonalFlight.objects.filter(is_active=True, start_date__lte=end_date, end_date__gte=start_date).select_related(
            "airline", "origin", "destination", "aircraft_type"
        )

        total_schedules = seasonal_flights.count()
        if total_schedules == 0:
            self.stdout.write(self.style.ERROR("✗ No active seasonal flights found for this period!"))
            return

        self.stdout.write(f"📋 Found {total_schedules} active seasonal schedules")

        created_count = 0
        skipped_count = 0
        error_count = 0

        # Generate flights day by day
        current_date = start_date

        with transaction.atomic():
            while current_date <= end_date:
                # Get day of week (1=Monday, 7=Sunday)
                day_of_week = current_date.isoweekday()

                # Find seasonal flights operating on this day
                for schedule in seasonal_flights:
                    # Check if schedule is valid for this date
                    if not (schedule.start_date <= current_date <= schedule.end_date):
                        continue

                    # Check if flight operates on this day of week
                    if str(day_of_week) not in schedule.days_of_operation:
                        continue

                    # Generate flight_id
                    flight_id = f"{current_date.strftime('%Y%m%d')}-{schedule.airline.iata_code}{schedule.flight_number}"

                    # Check if flight already exists
                    if incremental and DailyFlight.objects.filter(flight_id=flight_id).exists():
                        skipped_count += 1
                        continue

                    # Build departure and arrival DateTimes
                    stod = timezone.make_aware(datetime.combine(current_date, schedule.stod))
                    stoa = timezone.make_aware(datetime.combine(current_date, schedule.stoa))

                    # Handle flights that arrive next day
                    if schedule.stoa < schedule.stod:
                        stoa = timezone.make_aware(datetime.combine(current_date + timedelta(days=1), schedule.stoa))

                    if dry_run:
                        self.stdout.write(
                            f"   [DRY RUN] Would create: {flight_id} - "
                            f"{schedule.origin.iata_code}->{schedule.destination.iata_code} "
                            f"STD {stod.strftime('%H:%M')}"
                        )
                        created_count += 1
                    else:
                        try:
                            daily_flight, created = DailyFlight.objects.update_or_create(
                                flight_id=flight_id,
                                defaults={
                                    "schedule": schedule,
                                    "airline": schedule.airline,
                                    "flight_number": schedule.flight_number,
                                    "origin": schedule.origin,
                                    "destination": schedule.destination,
                                    "aircraft_type": schedule.aircraft_type,
                                    "date_of_operation": current_date,
                                    "status": "SCH",
                                    "stod": stod,
                                    "stoa": stoa,
                                    "is_manually_modified": False,
                                    "schedule_version": 1,
                                    "last_propagated_at": timezone.now(),
                                },
                            )

                            if created:
                                created_count += 1
                            else:
                                # Update existing but only if not manually modified
                                if not daily_flight.is_manually_modified:
                                    skipped_count += 1
                                else:
                                    skipped_count += 1

                            if created_count % 100 == 0:
                                self.stdout.write(f"   ✓ Created {created_count} flights...")

                        except Exception as e:
                            error_count += 1
                            if error_count <= 5:
                                self.stdout.write(self.style.WARNING(f"   ⚠ Error creating {flight_id}: {str(e)}"))

                current_date += timedelta(days=1)

        # Summary
        self.stdout.write("\n" + "=" * 60)
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"✓ DRY RUN: Would create {created_count} daily flights"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✓ Created {created_count} daily flights"))

        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f"⚠ Skipped {skipped_count} flights (already exist or manually modified)"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"✗ Failed {error_count} flights"))
        self.stdout.write("=" * 60 + "\n")

        # Statistics
        if not dry_run:
            total_daily = DailyFlight.objects.filter(date_of_operation__gte=start_date, date_of_operation__lte=end_date).count()
            manual_count = DailyFlight.objects.filter(
                date_of_operation__gte=start_date, date_of_operation__lte=end_date, is_manually_modified=True
            ).count()

            self.stdout.write("📊 Statistics:")
            self.stdout.write(f"   Total daily flights in period: {total_daily}")
            self.stdout.write(f"   Manually modified flights: {manual_count}")
            self.stdout.write(f"   Auto-propagatable flights: {total_daily - manual_count}\n")
