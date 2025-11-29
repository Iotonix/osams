# Daily Flight Form Performance Issues

## Problem

The edit form takes **4-6 seconds** to load, which is unacceptable.

## Root Cause

Django's default `<select>` widget renders **793 `<option>` tags** synchronously:

- Airlines: 94 options
- Airports (origin): 122 options  
- Airports (destination): 122 options
- Aircraft Types: 230 options
- Gates: 38 options
- Stands: 20 options
- Check-in Counters: 150 options
- Carousels: 17 options

At ~5ms per option, this takes **~4 seconds of pure HTML rendering time**.

## Optimizations Already Applied

1. ✅ **Cached ID queries** - Avoid repeated DB queries (5-minute cache)
2. ✅ **Filter by actual usage** - Load only 94 airlines (not 831), 122 airports (not 6,067)
3. ✅ **select_related in view** - Reduce N+1 queries when loading instance
4. ✅ **Added logging** - Track view load time vs HTTP response time

## Current Performance

- View loads in: **~1 second** (queries + Python)
- HTML renders in: **~4 seconds** (Django template engine)
- **Total**: ~5 seconds

## Recommended Solutions

### Option 1: django-select2 (Best Solution)

Install AJAX autocomplete for large dropdowns:

```bash
pip install django-select2
```

Replace large dropdowns (airlines, airports, aircraft) with Select2 widgets that load options dynamically.

**Expected improvement**: Under **1 second** load time

### Option 2: Raw ID Fields (Admin-style)

Use text input + lookup button (like Django admin):

- Shows ID number in text field
- Click button to open popup search window
- Good for power users, not end users

### Option 3: Limit Options Further

Only show airlines/airports/aircraft from the **currently visible date range** (e.g., today ± 7 days):

```python
# In form __init__
from datetime import date, timedelta
date_range = (date.today() - timedelta(days=7), date.today() + timedelta(days=7))
recent_airline_ids = DailyFlight.objects.filter(
    date_of_operation__range=date_range
).values_list('airline_id', flat=True).distinct()
```

**Expected improvement**: ~50% reduction in options → **~2 seconds**

### Option 4: Defer Non-Essential Fields

Split form into "Essential" and "Advanced" sections with collapsible accordion.
Load resources (gates, stands, check-ins, carousels) only when expanded.

## Testing Commands

```bash
# Check how many records in each dropdown
python manage.py shell -c "
from masterdata.models import Airline, Airport, AircraftType
print(f'Airlines (active): {Airline.objects.filter(is_active=True).count()}')
print(f'Airports (active): {Airport.objects.filter(is_active=True).count()}')
print(f'Aircraft (active): {AircraftType.objects.filter(is_active=True).count()}')
"

# Time the form creation
python manage.py shell -c "
import time
from flight_ops.forms import DailyFlightForm
from flight_ops.models import DailyFlight

flight = DailyFlight.objects.first()
start = time.time()
form = DailyFlightForm(instance=flight)
print(f'Form created in {(time.time()-start)*1000:.0f}ms')
"
```

## Decision

For production use, implement **django-select2** for airlines, airports, and aircraft type fields.
