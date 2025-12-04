# **Task: Implement Resource Allocation Timeline (Vis.js) in new Django App**

**Context:**
We are building an Open Source Airport Management System (OS-AMS) using **Django 5** and **Bootstrap 5**.
We are creating a new app called **`resource_mgmt`** to handle resource visualization using the **Vis.js Timeline** library.

**Goal:**
Generate the complete code for the `resource_mgmt` app to display a "Daily Operations Timeline" where flight bars are shown on Gate, Stand, and Check-in rows.

## **1. Data Model Context (Read-Only)**

You will need to query these existing models. Do not modify them, just import and use them.

* **`masterdata.models`**:
  * `Terminal` (Fields: `id`, `code`, `name`) - Parent container.
  * `Gate` (Fields: `id`, `code`, `terminal_id`) - Linked to Terminal.
  * `Stand` (Fields: `id`, `code`) - Remote parking (no terminal link usually).
  * `CheckInCounter` (Fields: `id`, `code`, `terminal_id`, `counter_group`) - Linked to Terminal. `counter_group` is a string like "Row A".
* **`flight_ops.models`**:
  * `DailyFlight` (The items to display)
    * `flight_id` (String), `airline` (FK), `flight_number` (String), `registration` (String).
    * `status` (Choices: SCH, OFB, AIR, LND, ONB, FIB, LSB, CXX, DIV).
    * **Timings:** `stod` (Sched Dep), `atod` (Actual Dep), `stoa` (Sched Arr), `aibt` (Actual Block In).
    * **Resources:** `gate` (FK to Gate), `stand` (FK to Stand), `checkin_counters` (ManyToManyField to CheckInCounter).

## **2. Implementation Requirements**

Please generate the code for the following three files:

### **File 1: `resource_mgmt/urls.py`**

* Define `app_name = 'resource_mgmt'`.
* Add two paths:
    1. `timeline/` -> `views.timeline_view` (The HTML page).
    2. `api/timeline-data/` -> `views.timeline_data` (The JSON endpoint).

### **File 2: `resource_mgmt/views.py`**

**A. `timeline_view(request)`**:

* Simply render `resource_mgmt/timeline.html`.
* Pass the current date as a string context variable `today` (format YYYY-MM-DD).

**B. `timeline_data(request)`**:

* **Input:** Accept a GET parameter `date` (default to today).
* **Output:** Return a `JsonResponse` with `{ "groups": [...], "items": [...] }`.

**Logic for `groups` (The Y-Axis):**

1. **Unassigned Group:** Create a group ID `"unassigned"` at the very top for flights with no Gate/Stand.
2. **Terminal Hierarchy:** Iterate through all active Terminals.
    * Create a Level 1 group for the **Terminal** (id: `term_X`).
    * **Gates:** Create Level 2 groups for all active **Gates** belonging to this terminal (id: `gate_X`). Parent is `term_X`.
    * **Check-in Rows:** Group counters by their `counter_group` field (e.g., "Row A").
        * Create Level 2 groups for these **Rows** (id: `row_X_Name`). Parent is `term_X`.
        * Create Level 3 groups for the actual **Counters** (id: `cntr_X`). Parent is the Row group ID.
3. **Stands:** Create a generic parent group "Apron/Stands" and put all **Stand** objects as children (id: `stand_X`).

**Logic for `items` (The Flights):**

1. Query `DailyFlight` for the selected date. Use `select_related` and `prefetch_related` for performance.
2. **Mapping Logic:**
    * **Start Time:** Use `aibt` (Actual In-Block) if present, else `stoa`.
    * **End Time:** Use `atod` (Actual Off-Block) if present, else `stod`.
    * **Label:** `{airline_code}{flight_number}`.
    * **Classes:** Add CSS class based on status (e.g., `item-sch`, `item-lnd`, `item-cxx`).
3. **Item Creation (One flight might result in multiple items):**
    * **Gate/Stand Item:** If `gate` is set, create item in group `gate_X`. If `stand` is set, create item in group `stand_X`. If neither, create item in group `"unassigned"`.
    * **Check-in Items:** Iterate through `flight.checkin_counters.all()`. Create an item for *each* counter in group `cntr_X`. (Time logic: Check-in opens 3 hours before STD, closes 40 mins before STD).

### **File 3: `templates/resource_mgmt/timeline.html`**

* Extend `base.html`.
* **Structure:**
  * A toolbar with a Date Picker (`<input type="date">`) and a "Load" button.
  * A container div `#visualization` for the timeline.
* **Libraries:** Include Vis.js Timeline CSS/JS via CDN (unpkg).
* **CSS:** Add custom styles in `{% block extra_css %}`:
  * `group-terminal`: Dark grey background, bold white text.
  * `group-row`: Light grey background, bold text.
  * `item-sch` (Blue), `item-lnd` (Green), `item-cxx` (Red/Striped).
  * `vis-item`: Small font size (11px).
* **JavaScript (`{% block extra_js %}`):**
  * Initialize `vis.Timeline`.
  * **Config:** `stack: true`, `stackSubgroups: true`, `orientation: 'top'`, `verticalScroll: true`, `maxHeight: '800px'`.
  * **AJAX:** Fetch data from the API when the Date Picker changes or "Load" is clicked.
  * **Interaction:** Add an `onMove` callback that logs to console: "Moved flight [ID] to group [GroupID]" (placeholder for future save logic).
