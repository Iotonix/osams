# Q&A Log - Gate Allocation Strategy Implementation

## Q1: Stand Allocation Priority and Logic
**Question:** For the `preferred_stand` field in SeasonalFlight - should stands be used as:
1. A backup when the gate is unavailable?
2. For specific flight types (cargo, long layovers)?
3. Both scenarios?

What's the business rule for when a stand vs gate should be allocated?

**Answer:** 3. Both scenarios (Hybrid Approach).

In the OS-AMS architecture, `preferred_stand` in SeasonalFlight serves a dual purpose:
- **Overflow/Backup:** For passenger flights (Service Type 'J'), the logic should be: Try preferred_gate first. If unavailable/occupied, fall back to preferred_stand.
- **Primary Assignment:** For Cargo flights (Service Type 'F') or technical stops, the preferred_gate should likely be null, making preferred_stand the primary resource.

**Business Rule:**
- IF service_type == 'Passenger' AND preferred_gate is valid: Allocate Gate.
- ELSE: Allocate Stand.

## Q2: Validation Timing - Seasonal vs Daily
**Question:** The AI.md specifies:
- **Seasonal:** Validate static constraints only (gate size, terminal, aircraft compatibility)
- **Daily:** Validate dynamic constraints (time conflicts, maintenance)

Should we:
1. Allow seasonal flights to be saved with validation warnings (soft validation)?
2. Block saving if hard constraints fail at seasonal level?
3. Show warnings but allow override with a "Force Save" option?

**Answer:** 2. Block saving if hard constraints fail at seasonal level.

Referencing RESOURCE_ALLOCATION_STRATEGY.md Section 1:
- **Seasonal (Static Constraints):** These represent physical impossibilities (e.g., trying to park a Code F aircraft on a Code C gate). This should be a **Hard Constraint** that raises a ValidationError and blocks saving. It prevents "impossible plans" from entering the system.
- **Daily (Dynamic Constraints):** Time overlaps are operational realities (delays). These should be **Soft Constraints** (warnings) at the point of generation, allowing the flight to be created even if conflict exists (to be resolved by the human controller).

## Q3: Terminal Matching - Hard or Soft Constraint?
**Question:** AI.md says terminal matching is "ideal" but exceptions exist (bussing). Should terminal mismatch:
1. Block the assignment (hard constraint)?
2. Show a warning but allow it (soft constraint)?
3. Require a specific permission/flag to override?

**Answer:** 2. Show a warning but allow it (Soft Constraint).

While RESOURCE_ALLOCATION_STRATEGY.md lists Terminal Matching as a constraint, operational reality often requires exceptions (e.g., bussing passengers from Terminal 1 to a remote stand near Terminal 2).

**Logic:** If SeasonalFlight.origin (Airport) implies a terminal context that implies a specific handling area, but the Gate is elsewhere, display a warning in the Admin UI: "Warning: Gate A1 is in Terminal 1, but flight is associated with Terminal 2 operations." Do not block the save.

## Q4: Resource Conflict Detection - Phase 1 Scope
**Question:** The document mentions a future "Conflict Detection Engine" (Phase 3). For the initial implementation (Phase 1-2), should we:
1. Just implement the data model and generation logic (no conflict detection yet)?
2. Implement basic overlap detection during save?
3. Add a management command to report conflicts after generation?

**Answer:** 1. Just implement the data model and generation logic.

The RESOURCE_ALLOCATION_STRATEGY.md explicitly places Conflict Detection in Phase 3.

**Strategy:** For Phase 1 & 2, focus purely on the pipeline: getting data from SeasonalFlight -> DailyFlight.

**Interim Solution:** Rely on the uniqueness of the data model and simple database queries to find issues manually if needed. Do not build a complex engine yet.

## Q5: Multiple Resource Assignment
**Question:** Looking at DailyFlight model, I see:
- `gate` (ForeignKey - single)
- `stand` (ForeignKey - single)
- `checkin_counters` (ManyToMany - multiple)

Should SeasonalFlight also support:
1. Multiple preferred check-in counters?
2. Multiple preferred carousels?
3. Or keep it simple with just gate + stand for Phase 1?

**Answer:** 3. Keep it simple with just gate + stand for Phase 1.

- **Gate/Stand:** Keep as ForeignKey (Single resource per flight event). Complex scenarios (tow-on/tow-off) can be handled later by splitting flights or adding specific "Movement" models.
- **Check-in:** Deferred. Check-in allocation is usually done by "Zone" or "Row" seasonally, not specific counters. Managing a ManyToMany relationship on the seasonal template is complex UI work. Stick to Gate/Stand for the MVP.

## Q6: Preferred Carousel Field
**Question:** The AI.md doesn't mention `preferred_carousel` but DailyFlight has a carousel field. Should we add:
- `preferred_carousel` to SeasonalFlight model?
- Logic to copy it during daily generation?

**Answer:** Yes, add it.

Although not explicitly in the markdown, it follows the exact same "Template & Instance" pattern.

**Action:** Add `preferred_carousel` (ForeignKey to BaggageCarousel) to SeasonalFlight.

**Logic:** Update generate_daily_flights to copy this field just like gates. This is a low-effort, high-value addition for the MVP.

## Q7: Migration Strategy and Data Preservation
**Question:** When adding the new fields (preferred_gate, preferred_stand) to SeasonalFlight:
1. Should we create a data migration to analyze existing DailyFlight assignments and backfill "common" gates to seasonal records?
2. Leave all existing seasonal flights with null preferred resources?
3. Provide a management command to suggest preferred resources based on historical data?

**Answer:** 2. Leave existing seasonal flights with null preferences.

**Rationale:** "Guessing" preferred gates based on history is risky and prone to errors.

**Strategy:** Make the new fields `null=True, blank=True`. Existing schedules will simply have no defaults (defaulting to unassigned in daily ops). Airlines/Admins can manually update the seasonal templates for the next schedule generation cycle.

## Q8: UI/Admin Interface Updates
**Question:** Should we update the Django Admin interface for SeasonalFlight to:
1. Show real-time validation feedback when selecting preferred_gate (AJAX checks)?
2. Filter gate/stand dropdowns to only show compatible options?
3. Keep it simple with standard dropdowns and validation on save?

**Answer:** 3. Keep it simple with standard dropdowns + Validation on Save.

**Rationale:** Implementing AJAX real-time checks adds significant frontend complexity.

**Phase 1 Approach:** Use Django's standard `clean()` method in admin.py. If a user selects an invalid gate, the form will fail validation on "Save" and display the error message defined in your models.py clean method. This is standard Django behavior and very robust. Use `autocomplete_fields` for the dropdowns to handle performance (solved by your existing select2 setup).

## Q9: Conflict Visualization Requirements
**Question:** For Phase 3 conflict detection, what's the expected UI:
1. Gantt chart view showing resource timeline (requires custom frontend)?
2. Simple list/table of conflicts with datetime ranges?
3. Calendar view with overlapping flights highlighted?

This helps determine if we need to structure data/queries differently now.

**Answer:** 1. Gantt chart view.

You already have `osams/code_snippets/aiport_resource_view.html` which is a Vis.js Gantt chart. This is the correct target for Phase 3. The data structure you are building now (Daily Flights with Start/End times and Resource FKs) is exactly what that chart needs to render rows.

## Q10: Manual Override Tracking
**Question:** When a daily flight's gate is manually changed from the preferred default:
1. Should we track WHO made the change (add user field)?
2. Track WHY (add notes/reason field)?
3. Just keep the existing `is_manually_modified` boolean?

**Answer:** 3. Just keep the existing `is_manually_modified` boolean.

**Rationale:** Django Admin automatically tracks "Who" and "When" via the `django_admin_log` table (LogEntry model). You don't need to duplicate this in your operational model.

**Workflow:** If a user edits a daily flight, your existing save_model override sets `is_manually_modified=True`. The history link in the admin page shows who did it.

## Q11: Gate/Stand Availability Status
**Question:** I see `is_available` fields on Gate and Stand models. Should the daily generation:
1. Respect is_available=False and skip those resources?
2. Copy preferred resources regardless and let ops staff deal with it?
3. Fall back to an alternative algorithm when preferred is unavailable?

**Answer:** 2. Copy preferred resources regardless (with warning).

**Reasoning:** Seasonal generation looks 90 days ahead. A gate might be `is_available=False` today for maintenance, but it might be open in 40 days when the flight happens.

**Logic:** Copy the `preferred_gate` to the DailyFlight. When the Daily Operations team looks at the flight 24 hours prior, that is when they should check availability and reassign if necessary.

## Q12: Validation Error Handling in Generation Command
**Question:** When `generate_daily_flights` command copies preferred_gate that violates dynamic constraints:
1. Skip that flight and log an error?
2. Copy it anyway and mark for manual review?
3. Attempt to find an alternative compatible gate automatically?

**Answer:** 2. Copy it anyway and mark for manual review (or leave Null).

**Refinement:** If the preferred_gate violates a hard physical constraint (e.g., aircraft size changed seasonally but gate preference wasn't updated), the generator should:
1. Create the Daily Flight. (Never skip creating the flight itself).
2. Set Gate = None. (Do not assign the invalid gate).
3. Log a Warning in the command output: "Flight TG920 created but preferred Gate A1 invalid for A380. Left unassigned."