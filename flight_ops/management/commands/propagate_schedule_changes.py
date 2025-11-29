from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from flight_ops.models import DailyFlight
from schedules.models import SeasonalFlight


class Command(BaseCommand):
    help = "Propagate seasonal schedule changes to future daily flights"

    def add_arguments(self, parser):
        parser.add_argument(
            "--schedule-id",
            type=int,
            help="Specific SeasonalFlight ID to propagate",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Propagate all seasonal schedules",
        )
        parser.add_argument(
            "--from-date",
            type=str,
            default="today",
            help="Start propagation from date (YYYY-MM-DD or 'today')",
        )
        parser.add_argument(
            "--buffer-hours",
            type=int,
            default=48,
            help="Only propagate to flights more than X hours in future (default: 48)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without actually updating",
        )

    def handle(self, *args, **options):
        schedule_id = options["schedule_id"]
        propagate_all = options["all"]
        from_date_str = options["from_date"]
        buffer_hours = options["buffer_hours"]
        dry_run = options["dry_run"]

        if not schedule_id and not propagate_all:
            self.stdout.write(self.style.ERROR("✗ Please specify --schedule-id or --all"))
            return

        # Parse from date
        if from_date_str == "today":
            from_date = timezone.now().date()
        else:
            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            except ValueError:
                self.stdout.write(self.style.ERROR(f"✗ Invalid date format: {from_date_str}. Use YYYY-MM-DD"))
                return

        # Calculate buffer datetime
        buffer_datetime = timezone.now() + timedelta(hours=buffer_hours)

        self.stdout.write(self.style.WARNING(f"\n🔄 Propagating Seasonal Schedule Changes"))
        self.stdout.write(f"   From date: {from_date}")
        self.stdout.write(f"   Buffer: {buffer_hours} hours (only flights after {buffer_datetime.strftime('%Y-%m-%d %H:%M')})")
        if dry_run:
            self.stdout.write(self.style.WARNING("   DRY RUN - No changes will be made\n"))
        else:
            self.stdout.write("")

        # Get seasonal flights to propagate
        if schedule_id:
            try:
                seasonal_flights = [SeasonalFlight.objects.get(pk=schedule_id)]
                self.stdout.write(f"📋 Propagating single schedule: ID {schedule_id}")
            except SeasonalFlight.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"✗ SeasonalFlight with ID {schedule_id} not found!"))
                return
        else:
            seasonal_flights = SeasonalFlight.objects.filter(is_active=True, end_date__gte=from_date)
            self.stdout.write(f"📋 Propagating {seasonal_flights.count()} active seasonal schedules")

        updated_count = 0
        skipped_manual_count = 0
        skipped_buffer_count = 0
        error_count = 0

        with transaction.atomic():
            for schedule in seasonal_flights:
                # Find future daily flights linked to this schedule
                daily_flights = DailyFlight.objects.filter(schedule=schedule, date_of_operation__gte=from_date, stod__gte=buffer_datetime).select_related(
                    "airline", "origin", "destination"
                )

                self.stdout.write(
                    f"\n   Processing: {schedule.airline.iata_code}{schedule.flight_number} "
                    f"({schedule.origin.iata_code}->{schedule.destination.iata_code})"
                )
                self.stdout.write(f"   Found {daily_flights.count()} future flights")

                for daily_flight in daily_flights:
                    # Skip manually modified flights
                    if daily_flight.is_manually_modified:
                        skipped_manual_count += 1
                        if not dry_run:
                            self.stdout.write(f"      ⚠ SKIP {daily_flight.flight_id} on {daily_flight.date_of_operation} (manually modified)")
                        continue

                    # Calculate new times
                    new_stod = timezone.make_aware(datetime.combine(daily_flight.date_of_operation, schedule.stod))
                    new_stoa = timezone.make_aware(datetime.combine(daily_flight.date_of_operation, schedule.stoa))

                    # Handle next-day arrivals
                    if schedule.stoa < schedule.stod:
                        new_stoa = timezone.make_aware(datetime.combine(daily_flight.date_of_operation + timedelta(days=1), schedule.stoa))

                    # Check what would change
                    changes = []
                    if daily_flight.stod != new_stod:
                        changes.append(f"STD {daily_flight.stod.strftime('%H:%M')} → {new_stod.strftime('%H:%M')}")
                    if daily_flight.stoa != new_stoa:
                        changes.append(f"STA {daily_flight.stoa.strftime('%H:%M')} → {new_stoa.strftime('%H:%M')}")
                    if daily_flight.aircraft_type != schedule.aircraft_type:
                        changes.append(f"Aircraft {daily_flight.aircraft_type.icao_code} → {schedule.aircraft_type.icao_code}")

                    if not changes:
                        continue  # Nothing to update

                    if dry_run:
                        self.stdout.write(
                            f"      [DRY RUN] Would update {daily_flight.flight_id} on {daily_flight.date_of_operation}: {', '.join(changes)}"
                        )
                        updated_count += 1
                    else:
                        try:
                            # Update the daily flight
                            daily_flight.stod = new_stod
                            daily_flight.stoa = new_stoa
                            daily_flight.aircraft_type = schedule.aircraft_type
                            daily_flight.airline = schedule.airline
                            daily_flight.origin = schedule.origin
                            daily_flight.destination = schedule.destination
                            daily_flight.flight_number = schedule.flight_number
                            daily_flight.last_propagated_at = timezone.now()
                            daily_flight.schedule_version += 1
                            daily_flight.save()

                            updated_count += 1
                            self.stdout.write(f"      ✓ Updated {daily_flight.flight_id} on {daily_flight.date_of_operation}: {', '.join(changes)}")

                        except Exception as e:
                            error_count += 1
                            self.stdout.write(self.style.ERROR(f"      ✗ Error updating {daily_flight.flight_id}: {str(e)}"))

        # Summary
        self.stdout.write("\n" + "=" * 60)
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"✓ DRY RUN: Would update {updated_count} daily flights"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✓ Updated {updated_count} daily flights"))

        if skipped_manual_count > 0:
            self.stdout.write(self.style.WARNING(f"⚠ Skipped {skipped_manual_count} manually modified flights (preserved user changes)"))
        if skipped_buffer_count > 0:
            self.stdout.write(self.style.WARNING(f"⚠ Skipped {skipped_buffer_count} flights (within {buffer_hours}h buffer)"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"✗ Failed {error_count} updates"))
        self.stdout.write("=" * 60 + "\n")
