# OS-AMS Seasonal Flight Resource Allocation

**Complete Technical Documentation**  
*Last Updated: December 6, 2025*

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Model](#data-model)
4. [Allocation Algorithm](#allocation-algorithm)
5. [Validation Rules](#validation-rules)
6. [Management Commands](#management-commands)
7. [Usage Examples](#usage-examples)
8. [Future Enhancements](#future-enhancements)

---

## Overview

### Purpose

OS-AMS implements a **Pre-Allocation Strategy** for airport resource management. Instead of manually assigning gates, stands, and carousels to each daily flight, the system:

1. **Seasonal Planning**: Airlines negotiate and receive "preferred" resources stored in `SeasonalFlight` templates
2. **Daily Operations**: The system automatically copies these preferences to `DailyFlight` instances
3. **Dynamic Adjustments**: Operations staff can override allocations for delays, maintenance, or conflicts

### Key Benefits

- **~80% Pre-Allocation**: Most flights start with gate assignments based on seasonal agreements
- **Reduced Manual Work**: Operators handle exceptions, not routine assignments
- **Validated Assignments**: Physical constraints (wingspan, aircraft type) are validated at seasonal level
- **Audit Trail**: Manual changes are tracked with `is_manually_modified` flag

---

## Architecture

### The "Template & Instance" Pattern

```
SeasonalFlight (Template)              DailyFlight (Instance)
├── preferred_gate         ─────────>  ├── gate (copied nightly)
├── preferred_stand        ─────────>  ├── stand (copied nightly)
├── preferred_carousel     ─────────>  ├── carousel (copied nightly)
└── Validated ONCE                     └── Operational reality
```

### Constraint Validation Layers

| Layer          | When                  | Validates                          | Enforcement |
|----------------|-----------------------|------------------------------------|-------------|
| **Seasonal**   | Template save         | Physical constraints (wingspan, aircraft type) | **Hard** (blocks save) |
| **Daily**      | Generation time       | Operational constraints (time conflicts, maintenance) | **Soft** (warnings only) |

---

## Data Model

### SeasonalFlight Model

**Location**: `schedules/models.py`

```python
class SeasonalFlight(models.Model):
    # Identity
    airline = ForeignKey(Airline)
    flight_number = CharField(max_length=10)
    
    # Route
    origin = ForeignKey(Airport, related_name="dep_schedules")
    destination = ForeignKey(Airport, related_name="arr_schedules")
    
    # Equipment
    aircraft_type = ForeignKey(AircraftType)
    service_type = CharField(max_length=1)  # J=Passenger, F=Cargo
    
    # Timing (UTC)
    stod = TimeField()  # Scheduled Time of Departure
    stoa = TimeField()  # Scheduled Time of Arrival
    
    # Validity
    start_date = DateField()
    end_date = DateField()
    days_of_operation = CharField(max_length=7)  # "1234567" = daily, "135" = Mon/Wed/Fri
    
    # *** RESOURCE ALLOCATION FIELDS ***
    preferred_gate = ForeignKey(Gate, null=True, blank=True, on_delete=SET_NULL)
    preferred_stand = ForeignKey(Stand, null=True, blank=True, on_delete=SET_NULL)
    preferred_carousel = ForeignKey(BaggageCarousel, null=True, blank=True, on_delete=SET_NULL)
```

### Gate-Stand Relationship

**Location**: `masterdata/models.py`

```python
class Gate(models.Model):
    code = CharField(max_length=10, unique=True)  # "A1", "B12", "C3"
    terminal = ForeignKey(Terminal, on_delete=CASCADE)
    
    # *** CRITICAL: 1:1 Linked Stand ***
    stand = ForeignKey(Stand, on_delete=PROTECT, related_name="gate", null=True)
    
    # Restrictions
    allowed_aircraft_types = ManyToManyField(AircraftType, blank=True)
    max_wingspan_meters = DecimalField(max_digits=5, decimal_places=2)
    
    gate_type = CharField(max_length=10)  # CONTACT, REMOTE, BOTH
    is_active = BooleanField(default=True)
    is_available = BooleanField(default=True)
```

**Key Design Decision**: Each **contact gate** (A1-C10) has a **fixed linked stand** (A1 → Stand A1). When a gate is allocated, its stand is automatically assigned. This matches real airport operations where jetbridge gates have dedicated parking positions.

---

## Allocation Algorithm

### Overview

**Command**: `python manage.py allocate_seasonal_resources`  
**Location**: `schedules/management/commands/allocate_seasonal_resources.py`

### Algorithm Steps

#### 1. Resource Pool Separation

```python
# Separate gates by terminal type
domestic_gates = Gate.objects.filter(terminal__code='DOM')           # C1-C10
international_gates = Gate.objects.exclude(terminal__code='DOM')     # A1-A16, B1-B12

# Separate stands by type
passenger_stands = Stand.objects.exclude(code__istartswith='CARGO')  # R1-R23, M1-M2
cargo_stands = Stand.objects.filter(code__istartswith='CARGO')       # CARGO1, CARGO2
```

#### 2. Flight Classification

```python
# Determine if flight is domestic (Thailand ↔ Thailand)
is_domestic = (
    flight.origin.country == 'Thailand' and 
    flight.destination.country == 'Thailand'
)

# Select appropriate gate pool
gate_pool = domestic_gates if is_domestic else international_gates
```

#### 3. Gate Allocation (Round-Robin)

```python
def _find_compatible_gate(flight, gates, start_index):
    """
    Round-robin distribution for even resource usage.
    Validates wingspan and aircraft type restrictions.
    """
    for i in range(len(gates)):
        gate = gates[(start_index + i) % len(gates)]
        
        # Check allowed aircraft types (if restricted)
        if gate.allowed_aircraft_types.exists():
            if flight.aircraft_type not in gate.allowed_aircraft_types.all():
                continue
        
        # Check wingspan constraint
        if gate.max_wingspan_meters:
            if flight.aircraft_type.wingspan_meters > gate.max_wingspan_meters:
                continue
        
        return gate
    
    return None
```

#### 4. Stand Auto-Assignment

```python
# When gate is assigned, automatically assign its linked stand
if suggested_gate:
    flight.preferred_gate = suggested_gate
    
    # *** AUTOMATIC STAND LINKING ***
    if suggested_gate.stand:
        flight.preferred_stand = suggested_gate.stand  # A1 → Stand A1
```

#### 5. Standalone Stand Allocation

**Only for flights WITHOUT gate assignments:**

```python
if not flight.preferred_gate:
    # Cargo flights → Cargo stands only
    if flight.service_type == 'F':
        stand = _find_compatible_stand(flight, cargo_stands, index)
        flight.preferred_stand = stand
    
    # Passenger overflow → Remote stands
    else:
        stand = _find_compatible_stand(flight, passenger_stands, index)
        flight.preferred_stand = stand
```

#### 6. Carousel Allocation (Arrivals Only)

```python
# Only for flights arriving at home airport (BKK)
if flight.destination.iata_code == "BKK":
    carousel = carousels[carousel_index % len(carousels)]
    flight.preferred_carousel = carousel
```

### Round-Robin Distribution

The algorithm uses **modulo indexing** to evenly distribute load:

```python
# Track separate indices for domestic/international
domestic_gate_index = 0
international_gate_index = 0

# After each assignment
if is_domestic:
    domestic_gate_index = (gate_pool.index(assigned_gate) + 1) % len(gate_pool)
else:
    international_gate_index = (gate_pool.index(assigned_gate) + 1) % len(gate_pool)
```

This ensures gates are used evenly (e.g., A1 → A2 → A3 → ... → A16 → A1 → ...)

---

## Validation Rules

### Hard Constraints (Block Save)

**Validated in**: `SeasonalFlight.clean()` method

#### 1. Aircraft Type Compatibility

```python
if gate.allowed_aircraft_types.exists():
    if aircraft_type not in gate.allowed_aircraft_types.all():
        raise ValidationError(
            f"Aircraft {aircraft_type.icao_code} not allowed on Gate {gate.code}"
        )
```

**Example**: A380 cannot use a gate restricted to Code C aircraft (A320/B737)

#### 2. Wingspan Restriction (Gate)

```python
if gate.max_wingspan_meters:
    if aircraft_type.wingspan_meters > gate.max_wingspan_meters:
        raise ValidationError(
            f"Wingspan {aircraft_type.wingspan_meters}m exceeds "
            f"gate maximum {gate.max_wingspan_meters}m"
        )
```

**Example**: B747 (wingspan 64.4m) cannot use a gate limited to 52m

#### 3. Wingspan Restriction (Stand)

```python
if stand.max_wingspan_meters:
    if aircraft_type.wingspan_meters > stand.max_wingspan_meters:
        raise ValidationError(
            f"Wingspan {aircraft_type.wingspan_meters}m exceeds "
            f"stand maximum {stand.max_wingspan_meters}m"
        )
```

### Soft Constraints (Warnings)

#### Terminal Matching

```python
if gate.terminal != carousel.terminal:
    warnings.append(
        f"Warning: Gate {gate.code} is in {gate.terminal.code}, "
        f"but Carousel {carousel.code} is in {carousel.terminal.code}. "
        f"Passengers may need inter-terminal transfer."
    )
```

**Note**: This doesn't block save—passengers can be bussed between terminals

---

## Management Commands

### 1. Allocate Seasonal Resources

**Command**: `allocate_seasonal_resources`

```bash
# Preview allocation without applying changes
python manage.py allocate_seasonal_resources --preview

# Apply allocation to all unassigned flights
python manage.py allocate_seasonal_resources

# Force re-allocation (overwrite existing assignments)
python manage.py allocate_seasonal_resources --force

# Allocate only specific airline
python manage.py allocate_seasonal_resources --airline TG
```

**Output**:
```
🎯 Seasonal Resource Auto-Allocation
Mode: APPLY

📋 Processing 1138 seasonal flights

  3K100 (DC94) → Gate:A1/A1(INTL)
  3K102 (E290) → Gate:A11/A11(INTL), Carousel:DOM-C1
  8B102 (B74D) → Gate:C1/C1(DOM)
  ...

============================================================
✓ Resource Allocation Complete
   Gates assigned: 1138
   Stands assigned: 0
   Carousels assigned: 571
============================================================
```

### 2. Link Gates to Stands

**Command**: `link_gates_to_stands`

```bash
# Show current gate-stand links
python manage.py link_gates_to_stands

# Auto-create stands matching gate codes
python manage.py link_gates_to_stands --auto-create
```

**What it does**:
- Creates Stand A1 → Links to Gate A1
- Creates Stand B12 → Links to Gate B12
- Determines `size_code` from gate's `max_wingspan_meters`

### 3. Print Seasonal Flights

**Command**: `print_seasonal_flights`

```bash
# View all flights (1 line per flight)
python manage.py print_seasonal_flights

# Filter by airline
python manage.py print_seasonal_flights --airline 3K

# Search flights
python manage.py print_seasonal_flights --search "SIN"
```

**Output**:
```
📋 Seasonal Flights (1138 flights)
========================================================================================================================
3K100    | BKK->SIN    | DC94 | Gate:A1(T1), Stand:A1                         | DEP:14:30 ARR:16:53  | 27-Oct-25 to 28-Mar-26  | 1234567
3K102    | SIN->BKK    | E290 | Gate:A11(T1), Stand:A11, Carousel:DOM-C1      | DEP:14:15 ARR:16:38  | 27-Oct-25 to 28-Mar-26  | 1234567
8B102    | BKK->HKT    | B74D | Gate:C1(DOM), Stand:C1                        | DEP:06:00 ARR:07:15  | 27-Oct-25 to 28-Mar-26  | 1234567
```

### 4. Generate Daily Flights

**Command**: `generate_daily_flights`

```bash
# Generate next 7 days (copies preferred resources)
python manage.py generate_daily_flights --days 7

# Preview without creating records
python manage.py generate_daily_flights --days 7 --dry-run
```

**Logic**:
```python
# Copy preferred resources from seasonal template
daily_flight = DailyFlight.objects.create(
    gate=seasonal.preferred_gate,           # Copy
    stand=seasonal.preferred_stand,         # Copy
    carousel=seasonal.preferred_carousel,   # Copy
    is_manually_modified=False
)

# Validation: If preferred_gate invalid for aircraft, set to None + log warning
```

---

## Usage Examples

### Scenario 1: Initial Allocation

```bash
# 1. Link all gates to their stands
python manage.py link_gates_to_stands --auto-create

# Output: Created 38 stands (A1-A16, B1-B12, C1-C10)

# 2. Allocate all seasonal flights
python manage.py allocate_seasonal_resources

# Output: 
#   Gates assigned: 1138
#   Carousels assigned: 571 (arrivals only)
```

### Scenario 2: Add New Airline

```bash
# Airline starts operations with 10 new flights
# System admin enters SeasonalFlight records via Django Admin

# Run allocation for just that airline
python manage.py allocate_seasonal_resources --airline 5X

# Output: 
#   Gates assigned: 10
#   (Uses round-robin to avoid overloading specific gates)
```

### Scenario 3: Seasonal Change

```bash
# Preview what would be re-allocated
python manage.py allocate_seasonal_resources --preview --force

# Review output, then apply
python manage.py allocate_seasonal_resources --force

# This overwrites existing assignments (use carefully!)
```

### Scenario 4: Daily Operations

```bash
# Every night at 02:00 (cron job):
python manage.py generate_daily_flights --days 90

# This creates DailyFlight instances for the next 90 days
# Each DailyFlight starts with preferred_gate/stand/carousel
# Operations staff adjust as needed during the day
```

---

## Current State (December 2025)

### ✅ Implemented (Phase 1 & 2)

- **Data Model**: `preferred_gate`, `preferred_stand`, `preferred_carousel` fields added to `SeasonalFlight`
- **Validation**: Hard constraints (wingspan, aircraft type) enforced at seasonal level
- **Gate-Stand Linking**: 1:1 relationship with automatic stand assignment
- **Allocation Algorithm**: Round-robin with domestic/international terminal separation
- **Management Commands**: `allocate_seasonal_resources`, `link_gates_to_stands`, `print_seasonal_flights`
- **Generation Logic**: `generate_daily_flights` copies resources from seasonal templates
- **UI Updates**: Django Admin forms with autocomplete, web view with resource display

### Statistics

| Resource Type | Total Available | Allocated Flights |
|---------------|-----------------|-------------------|
| Gates (A1-A16) | 16 | Used in round-robin |
| Gates (B1-B12) | 12 | Used in round-robin |
| Gates (C1-C10) | 10 | Used for domestic only |
| Contact Stands | 38 | Auto-assigned with gates |
| Remote Stands | 16 | For overflow/no gate |
| Cargo Stands | 2 | For cargo flights only |
| Carousels | 15 | Assigned to arrivals |
| **Total Seasonal Flights** | **1,138** | **100% allocated** |

### Terminal Distribution

| Terminal | Type | Gates | Flights Assigned |
|----------|------|-------|------------------|
| Terminal 1 - International | INTL | A1-A16 | ~650 |
| Terminal 2 - International | INTL | B1-B12 | ~390 |
| Domestic Terminal | DOM | C1-C10 | 98 (TH↔TH only) |

---

## Future Enhancements (Phase 3)

### 🔮 Planned Features

#### 1. Conflict Detection Engine

**Goal**: Identify time-based resource conflicts

```python
# Pseudo-code
def detect_conflicts():
    for gate in Gate.objects.all():
        flights = DailyFlight.objects.filter(gate=gate).order_by('stod')
        
        for i in range(len(flights) - 1):
            flight_a = flights[i]
            flight_b = flights[i + 1]
            
            # Check if A's estimated departure + turnaround > B's arrival
            if flight_a.etod + turnaround_time > flight_b.stoa:
                flag_conflict(flight_a, flight_b, gate)
```

**UI**: Red highlights in Gantt chart view

#### 2. Gantt Chart Visualization

**Existing**: `code_snippets/airport_resource_view.html` (Vis.js template)

**Data Structure Needed**:
```json
{
  "gate": "A1",
  "flights": [
    {
      "id": "TG920",
      "start": "2025-12-06T08:00:00Z",
      "end": "2025-12-06T09:30:00Z",
      "status": "on-time"
    },
    {
      "id": "BA123",
      "start": "2025-12-06T09:15:00Z",  // CONFLICT!
      "end": "2025-12-06T10:45:00Z",
      "status": "conflict"
    }
  ]
}
```

#### 3. Check-in Counter Allocation

**Deferred**: Check-in is typically allocated by "zone" or "row" seasonally, not specific counters.

#### 4. Smart Re-allocation

**Goal**: Automatically suggest alternative gates when conflicts detected

```python
# When Flight A delayed, find alternative gate for Flight B
alternative_gates = Gate.objects.filter(
    terminal=flight_b.preferred_gate.terminal,
    max_wingspan_meters__gte=flight_b.aircraft_type.wingspan_meters
).exclude(
    id__in=conflicting_gate_ids
)
```

---

## Technical Notes

### Why Round-Robin vs. AI/ML?

**Decision**: Use simple round-robin instead of optimization algorithms

**Rationale**:
1. **Predictability**: Operators understand the logic
2. **Even Wear**: All gates used equally (prevents maintenance concentration)
3. **Fast**: O(n) complexity, no complex calculations
4. **Good Enough**: For seasonal planning, exact optimization unnecessary

Future ML could optimize for:
- Passenger connection times
- Fuel costs (towing distance)
- Airline preferences (proximity to lounges)

### Database Performance

```sql
-- Indexes created by Django migrations
CREATE INDEX idx_seasonal_preferred_gate ON schedules_seasonalflight(preferred_gate_id);
CREATE INDEX idx_seasonal_preferred_stand ON schedules_seasonalflight(preferred_stand_id);
CREATE INDEX idx_seasonal_airline ON schedules_seasonalflight(airline_id);

-- Query optimization
SELECT * FROM schedules_seasonalflight
WHERE is_active = TRUE
  AND preferred_gate_id IS NULL
ORDER BY airline_id, flight_number;
-- Uses: idx_seasonal_preferred_gate, idx_seasonal_airline
```

### Migration History

| Migration | Description |
|-----------|-------------|
| `schedules.0002` | Added `preferred_gate`, `preferred_stand`, `preferred_carousel` fields |
| `masterdata.0007` | Added `Gate.stand` ForeignKey for 1:1 linking |

---

## Troubleshooting

### Issue: All flights assigned to same gate

**Symptom**: Round-robin not working, all flights get A1

**Cause**: Index not incrementing properly

**Fix**: Ensure index update happens AFTER assignment:
```python
gate_index = (gates.index(assigned_gate) + 1) % len(gates)
```

### Issue: International flights in domestic terminal

**Symptom**: SIN→BKK flights getting gates C1-C10

**Cause**: Terminal type detection not working

**Fix**: Check country comparison logic:
```python
is_domestic = (
    flight.origin.country == 'Thailand' and 
    flight.destination.country == 'Thailand'
)
```

### Issue: Passenger flights on CARGO stands

**Symptom**: Service type 'J' flights assigned to CARGO1, CARGO2

**Cause**: Stand pool not filtered

**Fix**: Exclude cargo stands from passenger pool:
```python
stands = Stand.objects.exclude(code__istartswith='CARGO')
```

---

## References

- **IATA SSIM**: Standard Schedules Information Manual (flight scheduling standards)
- **ICAO Aircraft Codes**: [ICAO Doc 8643](https://www.icao.int/publications/doc8643/)
- **Django Documentation**: [Model Validation](https://docs.djangoproject.com/en/5.0/ref/models/instances/#validating-objects)
- **Q&A Log**: See `questions.md` for detailed implementation decisions

---

**Document Version**: 1.0  
**Author**: OS-AMS Development Team  
**Contact**: See repository for issues and pull requests
