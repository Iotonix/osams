# Seasonal Flight Seeding

## Usage

### Seed Winter 2025/2026 Season

```bash
python manage.py seed_seasonal_flights --season winter2526 --clear
```

### Seed Summer 2026 Season

```bash
python manage.py seed_seasonal_flights --season summer2026 --clear
```

### Options

- `--season`: Choose season
  - `winter2526`: Oct 27, 2025 - Mar 28, 2026
  - `summer2026`: Mar 29, 2026 - Oct 24, 2026

- `--clear`: Delete existing seasonal flights for the season before seeding

- `--flights-per-route`: Average number of flight variations per route (1-3, default: 1)

### Examples

```bash
# Seed winter season with 1 flight per route
python manage.py seed_seasonal_flights --season winter2526 --clear

# Seed winter season with more flight variations (2-3 flights per route)
python manage.py seed_seasonal_flights --season winter2526 --clear --flights-per-route 2

# Seed summer season
python manage.py seed_seasonal_flights --season summer2026 --clear
```

## What It Does

1. **Reads all active routes** from the Route table
2. **Creates seasonal flights** for each route with:
   - Realistic flight numbers (100-999 per airline)
   - Frequency patterns: Daily (40%), Weekdays (30%), Selected days (25%), Weekends (5%)
   - Aircraft selection based on route distance
   - Departure times spread throughout the day
   - Calculated arrival times based on distance
3. **Hub routes** (from/to BKK) get more flights and daily frequency
4. **Bidirectional coverage** from existing routes

## Expected Output

For ~600 routes:

- **Hub routes**: 2-3 flights each (daily operation)
- **Other routes**: 1-2 flights each
- **Total**: ~600-1200 seasonal flights

## Frequency Distribution

- `1234567`: Daily (40%)
- `12345`: Weekdays (30%)
- `135`: Mon/Wed/Fri (15%)
- `246`: Tue/Thu/Sat (10%)
- `67`: Weekends (5%)
