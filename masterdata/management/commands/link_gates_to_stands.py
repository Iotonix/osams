from django.core.management.base import BaseCommand
from django.db import transaction

from masterdata.models import Gate, Stand


class Command(BaseCommand):
    help = "Link gates to their corresponding stands (e.g., Gate A1 → Stand A1)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--auto-create",
            action="store_true",
            help="Automatically create missing stands for gates",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing gate-stand links",
        )

    def handle(self, *args, **options):
        auto_create = options["auto_create"]
        force = options["force"]

        self.stdout.write(self.style.WARNING("\n🔗 Linking Gates to Stands"))
        self.stdout.write(f"Auto-create missing stands: {auto_create}")
        self.stdout.write(f"Force overwrite: {force}\n")

        gates = Gate.objects.all().select_related("stand")
        linked = 0
        created = 0
        skipped = 0
        errors = 0

        with transaction.atomic():
            for gate in gates:
                # Skip if already linked (unless force=True)
                if gate.stand and not force:
                    skipped += 1
                    continue

                # Try to find a stand with matching code
                stand = Stand.objects.filter(code=gate.code).first()

                if stand:
                    gate.stand = stand
                    gate.save()
                    linked += 1
                    self.stdout.write(f"  ✓ Linked Gate {gate.code} → Stand {stand.code}")
                elif auto_create:
                    # Create a new stand for this gate
                    try:
                        # Determine stand size based on gate's max wingspan
                        if gate.max_wingspan_meters:
                            wingspan = float(gate.max_wingspan_meters)
                            if wingspan >= 65:
                                size_code = "F"
                            elif wingspan >= 52:
                                size_code = "E"
                            elif wingspan >= 36:
                                size_code = "D"
                            elif wingspan >= 24:
                                size_code = "C"
                            elif wingspan >= 15:
                                size_code = "B"
                            else:
                                size_code = "A"
                        else:
                            size_code = "C"  # Default to Code C

                        stand = Stand.objects.create(
                            code=gate.code,
                            size_code=size_code,
                            max_wingspan_meters=gate.max_wingspan_meters or 35.80,
                            has_pushback=True,
                            is_active=gate.is_active,
                            is_available=gate.is_available,
                            notes=f"Auto-created for Gate {gate.code}",
                        )

                        gate.stand = stand
                        gate.save()
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f"  + Created Stand {stand.code} → Linked to Gate {gate.code}"))
                    except Exception as e:
                        errors += 1
                        self.stdout.write(self.style.ERROR(f"  ✗ Error creating stand for Gate {gate.code}: {e}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  ⚠ No stand found for Gate {gate.code} (use --auto-create to create)"))

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"✓ Linked: {linked} gates"))
        if created > 0:
            self.stdout.write(self.style.SUCCESS(f"+ Created: {created} stands"))
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f"⊘ Skipped: {skipped} (already linked)"))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f"✗ Errors: {errors}"))
        self.stdout.write("=" * 60 + "\n")
