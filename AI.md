# **OS-AMS Gate Allocation Strategy**

This document outlines the conceptual framework for managing Airport Resources (Gates, Stands, Check-in Counters) across both Seasonal Planning and Daily Operations.

## **1\. The Core Concept: "Default vs. Actual"**

To streamline daily operations, OS-AMS adopts a **Pre-Allocation Strategy**. Instead of starting every day with a blank slate (0% allocated), we aim to start with a \~80% complete plan based on seasonal agreements.

### **A. Seasonal Allocation (The "Default")**

* **Context:** Airlines negotiate slot usage and often request specific infrastructure (e.g., "British Airways always uses Gate A1").  
* **Mechanism:** We store preferred\_gate and preferred\_stand on the SeasonalFlight template.  
* **Validation:** At this stage, we validate **Static Constraints** only.  
  * *Is the gate large enough for this aircraft type?*  
  * *Is the gate in the correct terminal?*

### **B. Daily Allocation (The "Actual")**

* **Context:** The day of operation involves delays, weather, and maintenance.  
* **Mechanism:** The DailyFlight record has gate and stand fields.  
* **Initialization:** When the nightly generate\_daily\_flights command runs, it copies the *Seasonal Preferred Gate* \-\> *Daily Actual Gate*.  
* **Validation:** At this stage, we validate **Dynamic Constraints**.  
  * *Is the gate already occupied by a delayed flight?*  
  * *Is the gate under maintenance today?*

## **2\. Constraints & Compatibility Logic**

Airlines cannot simply choose any gate. The system must enforce compatibility rules defined in masterdata.

### **Hard Constraints (Must Pass)**

These checks prevent illegal assignments that would cause safety hazards or physical blocks.

1. **Aircraft Compatibility (Many-to-Many):**  
   * **Rule:** DailyFlight.aircraft\_type **MUST** be in Gate.allowed\_aircraft\_types.  
   * *Example:* An A380 cannot be assigned to a Code C (A320/B737) gate.  
2. **Wingspan Restriction:**  
   * **Rule:** AircraftType.wingspan\_meters **MUST** be \<= Gate.max\_wingspan\_meters.  
3. **Terminal Matching:**  
   * **Rule:** Ideally, Gate.terminal should match the flight's operational handling area, though exceptions exist (bussing).

## **3\. Implementation Plan**

### **Phase 1: Data Model Updates (schedules App)**

We need to enhance the SeasonalFlight model to store these preferences.

\# schedules/models.py

class SeasonalFlight(models.Model):  
    \# ... existing fields ...  
      
    \# NEW: Seasonal Preferences  
    preferred\_gate \= models.ForeignKey(  
        "masterdata.Gate",   
        null=True, blank=True,   
        on\_delete=models.SET\_NULL,  
        help\_text="The standard gate negotiated for this flight series."  
    )  
      
    preferred\_stand \= models.ForeignKey(  
        "masterdata.Stand",   
        null=True, blank=True,   
        on\_delete=models.SET\_NULL,  
        help\_text="Parking position if gate is not available or for long layovers."  
    )

    def clean(self):  
        \# Validation Logic (Pseudo-code)  
        if self.preferred\_gate and self.aircraft\_type:  
            \# 1\. Check Specific Allowed Types  
            if self.preferred\_gate.allowed\_aircraft\_types.exists():  
                if self.aircraft\_type not in self.preferred\_gate.allowed\_aircraft\_types.all():  
                    raise ValidationError(f"{self.aircraft\_type} not allowed on Gate {self.preferred\_gate}")  
              
            \# 2\. Check Wingspan  
            if self.preferred\_gate.max\_wingspan\_meters:  
                if self.aircraft\_type.wingspan\_meters \> self.preferred\_gate.max\_wingspan\_meters:  
                    raise ValidationError("Aircraft wingspan exceeds gate capacity")

### **Phase 2: Generation Logic Update (flight\_ops App)**

Update the management command generate\_daily\_flights.py to copy these values.

\# Inside the generation loop:  
defaults={  
    \# ... other fields ...  
    "gate": schedule.preferred\_gate,   \# Copy from template  
    "stand": schedule.preferred\_stand, \# Copy from template  
    "is\_manually\_modified": False,  
}

### **Phase 3: Conflict Detection (Future resource\_mgmt App)**

Assigning preferred\_gate seasonally creates a "Perfect World" plan. However, overlaps will occur (e.g., Flight A arrives late, blocking Flight B).

We will need a **Conflict Detection Engine** that runs:

1. **On Schedule Save:** Warn if the Seasonal Flight overlaps with another Seasonal Flight on the same gate (e.g., "Warning: TG920 overlaps with LH772 on Tuesdays").  
2. **On Daily Operations:** Visual alerts on the Gantt chart (Red Blocks) when actual times overlap on the same resource.

## **4\. Benefit Analysis**

| Feature | Without Seasonal Allocation | With Seasonal Allocation |
| :---- | :---- | :---- |
| **Daily Workload** | High. Controllers must assign gates for 300+ flights every morning. | Low. 90% of flights are auto-assigned. Controllers only manage exceptions. |
| **Consistency** | Low. Flight TG920 might be at A1 today, B5 tomorrow. | High. Passengers and Ground Crew learn that "TG920 is usually at A1". |
| **Planning** | Hard to visualize capacity. | Easy. We can see if Terminal 1 is "full" months in advance. |

