# **📘 OS-AMS User Guide & Standard Operating Procedures**

This guide outlines the standard workflows for managing airport operations using OS-AMS.

## **1\. Initial Setup (Master Data)**

Before scheduling flights, the physical and legal infrastructure of the airport must be defined.

### **1.1 Infrastructure Setup**

**Order of Operations:**

1. **Terminals:** Define physical buildings (e.g., "T1 International").  
2. **Stands:** Create parking positions.  
   * *Note:* Ensure Size Code matches the largest aircraft intended for that stand.  
3. **Gates:** Create boarding gates.  
   * **Crucial:** Link Gates to Stands if they are contact gates (Jetbridges).  
4. **Check-in & Carousels:** specific to terminals.

### **1.2 Aviation Data**

1. **Aircraft Types:** Ensure accurate dimensions (Wingspan/Length) as these drive the *Resource Allocation Engine*.  
2. **Airlines:** Create carrier profiles.  
3. **Routes:** Define valid connections (e.g., Airline TG flying BKK \-\> LHR).  
   * *Constraint:* You cannot create a schedule for a route that doesn't exist here.

## **2\. Scheduling Phase (Seasonal Planning)**

This phase typically happens 3-6 months before operations.

### **2.1 Creating Seasonal Flights**

Navigate to **Flight Planning \> Seasonal Schedules**.

* **Concept:** A "Seasonal Flight" is a template (e.g., "TG920 flies every Mon/Wed/Fri").  
* **Preferred Resources:** You can assign a Preferred Gate here. The system validates this against the aircraft type immediately. If the gate is too small, it will block the save.

### **2.2 Seeding (Bulk Creation)**

For setting up a new season quickly, ask your administrator to run the seeding command:  
python manage.py seed\_seasonal\_flights \--season winter2526

## **3\. Daily Operations Phase**

This is the day-to-day management of the airport.

### **3.1 Generating the Daily Schedule**

The system uses a **Rolling Window** strategy.

* **Automatic:** The system automatically generates flights for the next 90 days every night.  
* **Manual:** You can trigger this manually in **Flight Planning \> Daily Flights**.

### **3.2 Managing Live Flights**

Navigate to **Flight Operations \> Daily Flights**.

**Flight Status Workflow:**

1. **SCH (Scheduled):** The default state 24h+ out.  
2. **OFB (Off-Block):** Aircraft pushes back. *Actual Off-Block Time (AOBT)* is recorded.  
3. **AIR (Airborne):** Wheels up. *Actual Time of Departure (ATOD)* is recorded.  
4. **LND (Landed):** Touchdown. *Actual Time of Arrival (ATOA)* is recorded.  
5. **ONB (On-Block):** Arrived at gate/stand. *Actual In-Block Time (AIBT)* is recorded.

Status Codes Legend:  
| Code | Meaning | Context |  
|:---:|:---|:---|  
| SCH | Scheduled | Planned operation |  
| OFB | Off Block | Departures: Pushback complete |  
| AIR | Airborne | Departures: In flight |  
| LND | Landed | Arrivals: On runway |  
| ONB | On Block | Arrivals: Parked at gate |  
| FIB | First Bag | Arrivals: Baggage on belt |  
| LSB | Last Bag | Arrivals: Baggage complete |  
| CXX | Cancelled | Flight will not operate |  
| DIV | Diverted | Flight landed elsewhere |

### **3.3 Handling Exceptions (Resource Re-allocation)**

If a flight is delayed or a gate is closed:

1. Open the **Daily Flight** record.  
2. Change the **Gate** or **Stand**.  
3. **Note:** This sets the Manually Modified flag. Future automatic updates from the seasonal schedule will **ignore** this flight to preserve your changes.

## **4\. Resource Allocation Strategy**

OS-AMS uses a "Default \-\> Actual" logic.

1. **Pre-Allocation:** 90 days out, flights get their Preferred Gate from the seasonal plan.  
2. **Constraint Checks:** The system checks wingspan and airline exclusivity rules.  
3. **Conflict Management:** Currently, conflicts must be resolved manually by the Operations Controller.