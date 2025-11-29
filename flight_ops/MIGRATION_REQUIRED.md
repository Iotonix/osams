# Migration Required

After implementing the Rolling Window Strategy, you need to run:

```bash
python manage.py makemigrations flight_ops
python manage.py migrate
```

## New Fields Added to DailyFlight

1. `is_manually_modified` (BooleanField, default=False)
2. `schedule_version` (IntegerField, default=1)
3. `last_propagated_at` (DateTimeField, null=True)

These fields enable the Template & Instance pattern with smart propagation.
