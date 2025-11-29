# Daily Flight Generation - Rolling Window Strategy

## 🎯 Architecture Overview

This system implements the **"Template & Instance"** pattern with a **Rolling Window Strategy** to avoid the common aviation software trap of schedule fragmentation.

### Key Concepts

- **SeasonalFlight** (Template): The "Perfect Plan" - coordinated and approved seasonal schedules
- **DailyFlight** (Instance): The "Concrete Reality" - actual daily operations
- **Rolling Window**: Generate flights 90-180 days in advance
- **Dirty Flag Pattern**: Track manual modifications to prevent accidental overwrites

## 🚀 Management Commands

### 1. Generate Daily Flights

Creates DailyFlight records from SeasonalFlight templates for a rolling window period.

```bash
# Generate 90 days of flights (recommended for nightly cron)
python manage.py generate_daily_flights --days 90 --start-date today

# Generate specific date range
python manage.py generate_daily_flights --days 180 --start-date 2026-01-01

# Incremental mode (only create missing flights, skip existing)
python manage.py generate_daily_flights --days 90 --incremental

# Dry run to preview what would be created
python manage.py generate_daily_flights --days 90 --dry-run
```

**What it does:**

- Reads all active SeasonalFlights
- For each day in the window:
  - Checks day of week against `days_of_operation`
  - Creates DailyFlight with:
    - Link to parent SeasonalFlight
    - Calculated departure/arrival DateTimes
    - Status: "SCH" (Scheduled)
    - `is_manually_modified`: False
- **Idempotent**: Won't recreate existing flights

### 2. Propagate Schedule Changes

Updates future DailyFlights when SeasonalFlight changes (smart upstream propagation).

```bash
# Propagate specific schedule
python manage.py propagate_schedule_changes --schedule-id 123

# Propagate all schedules
python manage.py propagate_schedule_changes --all --from-date today

# With 72-hour buffer (only update flights >72h away)
python manage.py propagate_schedule_changes --all --buffer-hours 72

# Dry run to preview changes
python manage.py propagate_schedule_changes --schedule-id 123 --dry-run
```

**What it does:**

- Finds future DailyFlights linked to the SeasonalFlight
- For each flight:
  - **SKIPS** if `is_manually_modified=True` (preserves user customizations)
  - **SKIPS** if within buffer period (default 48 hours)
  - **UPDATES** if auto-propagatable: times, aircraft type, etc.
- Logs all changes and skips

## 📅 Automation Strategy

### Nightly Cron Job (00:30)

```bash
# Run every night to maintain 90-day rolling window
30 0 * * * cd /path/to/osams && python manage.py generate_daily_flights --days 90 --incremental
```

This ensures:

- "Today + 90 days" always has flights
- No duplicate creation (incremental mode)
- Automatic coverage of new seasonal schedules

### After Seasonal Schedule Updates

When airline updates their seasonal schedule:

```bash
# 1. Preview what will change
python manage.py propagate_schedule_changes --schedule-id 456 --dry-run

# 2. Review the output carefully

# 3. Apply changes
python manage.py propagate_schedule_changes --schedule-id 456
```

## 🛡️ Safety Features

### 1. Manual Modification Protection

**When you edit a DailyFlight:**

- Through UI: `is_manually_modified` automatically set to `True`
- Through Admin: `is_manually_modified` automatically set to `True`
- This flight is now **protected** from auto-propagation

**Use case:**

```
- Flight TG920 on 2026-02-15 needs aircraft change (A350 → B777)
- Edit the DailyFlight → is_manually_modified=True
- Later, airline changes SeasonalFlight times
- TG920 on 2026-02-15 keeps your B777 (not overwritten)
- Other dates get the new times (they're still auto-propagatable)
```

### 2. Buffer Period Protection

Default: **48 hours**

Only propagates to flights more than 48 hours in the future. Prevents accidentally changing:

- Flights already in operation
- Flights with crew/pax bookings locked in
- Near-term resource allocations

### 3. Audit Trail

Each DailyFlight tracks:

- `schedule_version`: Increments on each propagation
- `last_propagated_at`: Timestamp of last update
- Logs show exactly what changed

## 📊 Model Fields

### DailyFlight - Rolling Window Fields

```python
schedule = ForeignKey(SeasonalFlight)  # Parent template
is_manually_modified = BooleanField(default=False)  # Dirty flag
schedule_version = IntegerField(default=1)  # Version tracking
last_propagated_at = DateTimeField(null=True)  # Last update timestamp
```

## 🔄 Typical Workflows

### Workflow 1: Initial Setup

```bash
# 1. Seed seasonal flights
python manage.py seed_seasonal_flights --season winter2526 --clear

# 2. Generate 90 days of daily flights
python manage.py generate_daily_flights --days 90 --start-date today

# 3. Check results
python manage.py shell
>>> from flight_ops.models import DailyFlight
>>> DailyFlight.objects.count()
```

### Workflow 2: Seasonal Schedule Change

```bash
# Scenario: Airline changes TG920 departure time 10:00 → 10:15

# 1. Update SeasonalFlight in admin/UI (TG920: stod = 10:15)

# 2. Preview propagation
python manage.py propagate_schedule_changes --schedule-id 123 --dry-run

# Output shows:
#   ✓ Would update 85 flights
#   ⚠ Skipped 5 manually modified flights

# 3. Apply
python manage.py propagate_schedule_changes --schedule-id 123

# Result:
#   - 85 future flights updated to 10:15
#   - 5 manually customized flights untouched
```

### Workflow 3: Ad-hoc Flight Change

```bash
# Scenario: TG920 on 2026-03-15 needs different aircraft

# 1. Find the flight in admin or UI
# 2. Edit: Change aircraft A320 → A321
# 3. System auto-sets: is_manually_modified=True
# 4. This specific flight now immune to propagation
```

### Workflow 4: Daily Operations

```bash
# Every night at 00:30
python manage.py generate_daily_flights --days 90 --incremental

# This:
# - Checks "today + 90"
# - Creates flights if missing
# - Skips if already exist
# - Maintains rolling window automatically
```

## ⚠️ Important Notes

### Do NOT Split Seasons

**Bad Practice:**

```
# DON'T create 3 fragments:
SeasonalFlight: Oct 27 - Feb 14  (original)
SeasonalFlight: Feb 15 - Feb 15  (one-day change)
SeasonalFlight: Feb 16 - Mar 28  (original continued)
```

**Good Practice:**

```
# Keep one SeasonalFlight:
SeasonalFlight: Oct 27 - Mar 28

# Handle exceptions in DailyFlight:
DailyFlight(2026-02-15): is_manually_modified=True
```

### Propagation Safety

Always use `--dry-run` first when propagating changes to:

- See what will change
- Verify manual modifications are preserved
- Check buffer period is appropriate

### Window Size Recommendations

- **Start with 90 days** - Good balance
- **Extend to 180 days** once confident - More advance planning
- **Minimum 60 days** - Less than this defeats the purpose

## 🎛️ Admin Interface Features

### DailyFlight Admin

**List View:**

- Shows `is_manually_modified` column
- Filter by modification status
- Quick identification of custom flights

**Edit View:**

- Auto-sets `is_manually_modified=True` on save
- Shows schedule version and last propagation
- Rolling Window Strategy section (collapsible)

**Admin Actions:**

- "Propagate schedule changes" - Bulk update selected flights
- Respects manual modification flag
- Shows update/skip counts

## 📈 Monitoring

### Check Rolling Window Health

```python
from datetime import date, timedelta
from flight_ops.models import DailyFlight

# Check coverage
today = date.today()
end_date = today + timedelta(days=90)
count = DailyFlight.objects.filter(
    date_of_operation__gte=today,
    date_of_operation__lte=end_date
).count()

print(f"Flights in 90-day window: {count}")

# Check manual modifications
manual_count = DailyFlight.objects.filter(
    date_of_operation__gte=today,
    is_manually_modified=True
).count()

print(f"Manually modified: {manual_count}")
```

## 🔧 Troubleshooting

### Issue: Flights not generating

**Check:**

1. Are SeasonalFlights active? (`is_active=True`)
2. Do date ranges overlap? (`start_date` ≤ target ≤ `end_date`)
3. Is day of week correct? (`days_of_operation` contains weekday number)

### Issue: Propagation not working

**Check:**

1. Is flight within buffer period? (default 48 hours)
2. Is `is_manually_modified=True`? (by design, skipped)
3. Does DailyFlight have link to SeasonalFlight?

### Issue: Too many manual modifications

**Solution:**
If you need to "reset" a flight to auto-propagatable:

```python
flight = DailyFlight.objects.get(flight_id="20260315-TG920")
flight.is_manually_modified = False
flight.save()
```

Then run propagation to sync it.
