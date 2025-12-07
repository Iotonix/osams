
# **Architectural and Strategic Blueprint for an Open Source Airport Management System (OS-AIMS)**

This doc provides an expert-level architectural analysis and complete product requirements specification for developing a modular, highly scalable Open Source Airport Management System (OS-AMS) using the Django 5 framework. The design specifically targets the operational and financial needs of small-to-medium size airports (SMAs), focusing on maximizing efficiency and retiring reliance on expensive, proprietary legacy systems.

## **Section I: Foundational Architecture & Strategic Decisions**

### **1\. Analysis of Architectural Alternatives**

The initial stage of development requires critical decisions regarding the project’s structure, data persistence layer, and frontend tooling. These choices dictate the long-term maintainability, scalability, and suitability of the system for a complex enterprise domain like aviation management.

#### **1.1. Django App Structure: Modular Monolith vs. Single Application**

The choice between a single Django application or a modular structure fundamentally impacts project longevity. For small projects or proofs of concept, a single app simplifies the structure and reduces initial overhead.1 However, an Airport Management System, which encompasses critical and disparate domains such as scheduling, resource allocation, and billing, is inherently a large-scale enterprise application.

The recommendation is to adopt a **Modular Monolith architecture using multiple Django applications**.

Django applications are designed to encapsulate functionality related to a specific aspect of a project, promoting modularity, reusability, and scalability.1 While combining all operational and financial logic into one application is technically feasible, it would lead to code bloat, increased coupling, and significant technical debt as the project matures.2 Industry best practices for complex systems advocate for breaking down functionality into discrete, manageable units where each application "should do one thing and one thing alone".3

For the OS-AMS, the user-defined modules—Master Data, Schedules, Allocation, FIDS, Social Media, Billing/BI, and Integration—represent distinct business domains. Isolating these domains into separate applications simplifies independent testing, maintenance, and future expansion. For instance, the highly complex constraint-based logic of resource allocation can be contained within an allocation app, separate from the financial logic residing in the billing app. Furthermore, a foundational core application is necessary to house project-wide components such as abstract models, utility functions, and custom middleware.2 This organizational clarity is essential for a successful open-source project, facilitating developer onboarding and contribution.

#### **1.2. Database Stack: SQLite vs. PostgreSQL with Advanced Extensions**

The selection of the database backend is paramount for system integrity, performance, and scalability, particularly given the concurrent demands of real-time airport operations.

SQLite, while offering simplicity and ease of shipping for initial development, is fundamentally unsuitable for high-concurrency, server-based workloads involving large datasets and intricate queries.4 An AMS requires robust transactional integrity (ACID compliance) and efficient handling of simultaneous read/write operations across multiple operational users (e.g., tower, ground handling, billing).

The definitive recommendation is to utilize **PostgreSQL 16 or later, leveraging the TimescaleDB and PGvector extensions**.

##### **1.2.1. PostgreSQL as the Core**

PostgreSQL is tailored for robust, feature-rich systems with high scalability requirements. It excels in performance due to advanced indexing, query optimization, and architectural designs that avoid file-locking issues during concurrent writes, making it the superior choice for a mission-critical AMS.5

##### **1.2.2. The Necessity of TimescaleDB**

Airport operations generate vast amounts of time-series data: flight movement logs, gate utilization records, delay timestamps, and performance indicators.6 The financial and operational efficiency reporting required by the BI module depends entirely on rapid, efficient querying and aggregation of this historical data. Using standard PostgreSQL tables for this volume of temporal data would inevitably lead to performance bottlenecks. TimescaleDB, a PostgreSQL extension, solves this by specializing in time-series data management through hyper-tables, ensuring that complex analytical queries required by the bi\_stats application remain fast and scalable over years of accumulated operational history.6 This extension is not merely an optimization feature; it is a critical enabling component for the performance of the system’s core revenue and operational reporting functions.

##### **1.2.3. Strategic Value of PGvector**

The inclusion of the pgvector extension provides a crucial architectural layer for future advanced analytics and artificial intelligence integration.8 While the initial system focuses on deterministic logic (scheduling, billing rules), the aviation industry is rapidly moving toward predictive operations.9 PGvector allows the system to store and index high-dimensional vector embeddings, which can represent complex data patterns—such as the vector of factors leading to a particular flight delay or the characteristics of operational documents. This capability positions the OS-AMS to evolve beyond rule-based operations into an AI-powered system capable of predictive allocation, semantic search on operational manuals, or advanced pattern recognition in high-dimensional flight data.10

#### **1.3. Frontend Strategy: Core Bootstrap vs. Commercial ThemeForest Template**

The choice of frontend framework must align with the open-source licensing strategy (MIT) and the project's long-term maintainability.

**Building the UI on Core Bootstrap is the recommended approach.**

While a commercial ThemeForest template offers faster aesthetic completion via pre-designed HTML/CSS pages 11, these themes often carry restrictive commercial licenses or dependencies that conflict with the permissive nature of the MIT license. The MIT License guarantees maximum freedom, allowing reuse within proprietary software provided the license terms and copyright are included.12 Introducing proprietary or conditionally licensed frontend assets complicates distribution, creates potential legal risk for downstream commercial users, and hinders community contribution. Utilizing a standard, universally open-source framework like Bootstrap ensures licensing clarity and maximizes the ease of maintenance and integration by the global open-source community.13

### **2\. Core Technology Stack Specification and Insights**

#### **2.1. Django and Asynchronous Architecture for Real-Time Operations**

The operational requirement for a Flight Information Display System (FIDS) demands real-time communication that traditional Web Server Gateway Interface (WSGI) architectures cannot efficiently provide. FIDS is a critical system for passenger flow and safety, necessitating timely updates for flight status, gate changes, and delays.14

The system must operate using an **ASGI (Asynchronous Server Gateway Interface)** stack, specifically integrating **Django Channels** and a dedicated ASGI server like Daphne.16

This architecture is necessary to establish persistent, low-latency WebSocket connections with FIDS screens. Any update to a flight's status or assigned resource must instantly trigger a push notification through the Channels layer, ensuring that real-time information dissemination is reliable and sub-second.18 This approach ensures the FIDS maintains its function as a critical system with high availability and maximum reliability in its displays.14 This commitment to real-time performance mandates critical infrastructure dependencies, including a robust message broker (such as Redis or RabbitMQ) dedicated to the Channels layer, which must be configured alongside the primary database layer.

#### **2.2. Data Modeling Strategy and Structure**

The project structure must reflect the domain segregation discussed, translating the operational modules into discrete Django applications. This structural breakdown is summarized below:

| App Name | Core Functionality / Domain | Module Association | Rationale (Separation of Concerns) |
| :---- | :---- | :---- | :---- |
| core | Abstract models, utilities, middleware, custom exceptions 2 | Project-wide | Centralized configuration and shared components. |
| masterdata | Aircraft types, Gates, Terminals, Counters, Customer Profiles 19 | 1\. Master Data | Static, foundational reference data for the entire AMS. |
| schedules | Seasonal/Daily flight plans, SSIM import processing, Typical Day analysis | 2\. Flight Schedule | Handles IATA standards and complex temporal planning logic. |
| allocation | Constraint-based engine for Gates, Check-in, Baggage 20 | 3\. Resource Allocation | Optimization layer; highly complex operational logic. |
| fids | Real-time push logic, display templates, emergency override management 14 | 4\. FIDS | ASGI Consumers and WebSocket routing. |
| billing | Tariff engine, revenue calculation, contract management 23 | 6\. Billing/BI (Data Generation) | Financial integrity; requires strict data validation and audit trails. |
| bi\_stats | Dashboard visualization, KPI aggregation (using TimescaleDB queries) 24 | 6\. Billing/BI (Data Presentation) | Dedicated visualizations based on presentation best practices. |
| integrations | SSIM parser, SITA messaging (Type B/X) handlers, external API interfaces 26 | 7\. Integration | Isolates external communication protocols and complex parsing logic. |
| social\_updates | Social authentication, API connection, update push pipeline 28 | 5\. Social Media | Isolates external credentials and social API interaction logic. |

The interdependence between these modules must be managed via explicit foreign key relationships and signals, rather than tightly coupled business logic. The schedules app informs the allocation app, which then sends assignment results to the fids app for display and provides operational data to the billing app for revenue calculation.

## **Section II: Open Source Product Strategy and Market Pitch**

### **3\. The Open Source Airport Management Solution Pitch**

#### **3.1. Problem & Opportunity Statement**

Small-to-medium airports represent a significant, yet historically underserved, segment of the aviation infrastructure. These airports often rely on expensive, customized, monolithic legacy systems or inefficient manual processes that create substantial technical debt.29 These traditional proprietary systems demand high recurring licensing costs and prohibit rapid modernization or flexible integration necessary to support emerging trends like Advanced Air Mobility (AAM).29 The opportunity is to provide a modern, cost-effective, and fully featured alternative.

The OS-AMS, built on a robust Django/PostgreSQL foundation, offers SMAs the technological means to optimize operations, improve efficiency, and reduce operational costs by up to 30%, a significant metric in the cost-sensitive aviation industry.9

#### **3.2. Value Proposition and Market Fit**

The OS-AMS delivers three primary values:

1. **Cost Elimination:** By adopting the open-source MIT license, the system eliminates the primary barrier to entry—high-cost perpetual or subscription licensing fees—making advanced management tools accessible to budget-constrained regional airports.  
2. **Modernization and Extensibility:** The architecture is designed to handle the critical temporal data inherent to airport operations, leveraging TimescaleDB for highly efficient time-series analysis.6 Furthermore, the inclusion of pgvector future-proofs the system by creating a foundation for adopting predictive analytics and AI-driven optimization techniques, allowing these airports to leapfrog decades of technological stagnation.  
3. **Operational Optimization:** The Resource Allocation Engine (Module 3\) provides constraint-based logic to maximize the utilization of fixed resources (gates, counters) while adhering to complex operational constraints and optimizing passenger experience (e.g., minimizing walking distances).20

The core purpose of the project can be encapsulated in the following one-sentence pitch:

Table Title

| Component | Description |
| :---- | :---- |
| My company, | \*\*\*\*\*\*, |
| is developing | **a modular, real-time Airport Management System**, |
| to help | **small-to-medium airport operators**, |
| with | **optimizing resource allocation, automating aeronautical billing based on flexible tariffs, and retiring costly, complex legacy systems.** |

#### **3.3. Licensing Strategy: The MIT License Rationale**

The selection of the MIT License is a critical strategic decision that maximizes the commercial viability and adoption of the OS-AMS.

The MIT License is highly permissive and straightforward, providing minimal restrictions while allowing for free use, modification, and distribution of the software.31 This is crucial for an enterprise tool because it allows system integrators, ground handling agents, or airport IT departments to reuse the core OS-AMS code within their own proprietary software without any requirement to open-source their specific modifications or additions.12 This "reuse within proprietary software" feature makes the OS-AMS an attractive foundational component for commercial vendors and internal enterprise developers alike.

Furthermore, the simplicity of the license minimizes legal friction. It is widely adopted, compliant with the Debian Free Software Guidelines (FSG) and approved by the Free Software Foundation (FSF) and the Open Source Initiative (OSI), ensuring its credibility and acceptability across the industry.12 The only condition is the retention of the original copyright notice and license text in all copies, ensuring clear attribution without imposing burdensome copyleft restrictions.31

### **4\. Business Intelligence and ROI Proposition**

The Billing and BI (Business Intelligence) module (billing and bi\_stats apps) must move beyond simple data aggregation to provide actionable metrics that drive efficiency and revenue growth, essential for justifying the system's adoption.

#### **4.1. Key Performance Indicators (KPIs) and Analytics**

The BI module must centralize data from the schedules, allocation, and billing modules to calculate and display critical KPIs relevant to small-to-medium airports.32

Operational KPIs include:

* **On-Time Performance (OTP):** Calculated as the percentage of scheduled flights departing from the gate on time, often measured by variants such as departures within $\\pm 5$ minutes of the scheduled time.33  
* **Capacity Utilization:** Metrics detailing the usage rate of fixed resources (gates, counters) during reportable hours (the busiest hours of the day for the facility).34  
* **Safety Indicators:** Tracking operational safety metrics such as runway incursions per year and the number of accidents/incidents.24

Financial KPIs must focus on revenue generation and cost management:

* **Revenue per Operation:** Annual or monthly airport revenue normalized by the total number of itinerant operations, broken down by aircraft type (jet/piston).24  
* **Fuel Flow Revenue:** Tracking fuel flow revenue monthly by operation type, providing insight into non-aeronautical income streams.24  
* **Operating Expense Ratios:** Annual operating and maintenance expense normalized per operation.24

#### **4.2. Dashboard Design and Visualization**

Dashboard presentation in the bi\_stats app must adhere to strict data visualization best practices to ensure management can rapidly interpret performance metrics. The goal is to maximize the data-ink ratio—the amount of ink used to present data versus the total ink on the chart.25 Visualization design must:

* Utilize appropriate chart types (e.g., bar charts are preferred over pie charts for comparison, as human eyes struggle to detect exact size differences in 2-D or 3-D shapes).25  
* Avoid non-essential elements, including complex 3-D charts, which obscure the message and reduce clarity.25  
* Ensure the purpose of any visualization can be determined in less than 10 seconds.25

The foundation of the BI module’s performance relies directly on the PostgreSQL/TimescaleDB configuration. TimescaleDB’s ability to efficiently handle the temporal data of flight movements and resource usage prevents the critical billing calculations and subsequent KPI generation from becoming performance bottlenecks, maintaining system utility.

## **Section III: 100% Complete Product/Project Requirements Specifications (PRD)**

### **5\. Module 1 & 2: Master Data and Scheduling Management**

#### **5.1. Airport Master Data Requirements (masterdata app)**

The masterdata application serves as the authoritative source for all static, foundational data required by the operational modules.

##### **5.1.1. Physical Infrastructure Definitions**

Models must define physical assets with operational parameters:

* **Terminals:** Logical groupings of resources.  
* **Gates/Positions:** Must store attributes like physical dimensions, maximum supported aircraft types (compatibility constraint for allocation), and proximity metrics (e.g., walking distance to security/check-in).  
* **Check-in Counters and Baggage Belts:** Definition includes number of entries, capacity, and current operational status.

##### **5.1.2. Aircraft and Customer Master Data**

* **Aircraft Type:** Model must include IATA/ICAO designators, physical characteristics (wingspan, length), and critically, the Maximum Takeoff Weight (MTOW), which is a key price-influencing factor for aeronautical billing.23  
* **Customer Profiles:** Management of customer master data for airlines and ground handlers, including address, contact information, financial details, and storage for associated documents (e.g., customs permits, rental contracts).19

#### **5.2. Flight Schedule Management (schedules app)**

The schedules app manages the long-term planning and dynamic daily execution of flight operations, adhering to IATA standards.

##### **5.2.1. Schedule Data Structure and Types**

The system must handle both Seasonal Schedules (used for long-term planning) and Daily Operational Schedules (the dynamic state reflecting real-time changes). Core data elements include IATA standard flight details (carrier, flight number, city pairs), aircraft registration, and block times.35

##### **5.2.2. Scheduling Features**

* **Seasonal Copying:** Functionality to copy an entire season's flight plan (e.g., Summer 2025\) to a future season, enabling rapid planning cycles.  
* **Typical Day Filters:** Filters allowing planners to view and modify all operations specific to a defined day of the week, simplifying recurrent flight planning.  
* **Scenario Planning:** The ability to create sandboxed schedule modifications or resource assignments (scenarios) which can be tested against constraints and compared against the current operational plan before being activated.  
* **Minimum Connection Time (MCT) Management:** The system must define, store, and validate MCTs between arrival and connecting departure flights, ensuring schedule integrity and adherence to IATA standards.35

#### **5.3. Integration Requirement: SSIM Import Specification (integrations app)**

To ingest bulk flight schedule data from airlines and industry partners, the OS-AMS requires a specialized parser for the IATA Standard Schedules Information Manual (SSIM) file format.

The SSIM is a standardized flat file composed of fixed-length records, typically 200 bytes long.26 Standard Django file processing is inadequate for this fixed-width format. A custom, low-level Python parser must be developed within the integrations app, capable of reading and interpreting the sequential record types defined in SSIM Chapter 7\.26

* **Supported Record Types:** The parser must reliably process Header Record (Type 1), Carrier Record (Type 2), Flight Leg Record (Type 3), Segment Record (Type 4), and Trailer Record (Type 5).26  
* **Data Flow:** The parser extracts data elements (e.g., flight times, route) and performs essential data consistency and quality checks before mapping and committing the information to the schedules models.

### **6\. Module 3: Complex Resource Allocation Engine (allocation app)**

The allocation application is the operational heart of the AMS, responsible for assigning fixed resources—gates, check-in counters, and baggage belts—based on dynamic constraints and optimization goals.30

#### **6.1. Gate Allocation Constraints and Logic**

The primary objective of gate allocation is to maximize resource utilization while ensuring a high standard of customer service and airport safety.30

##### **6.1.1. Mandatory Constraints**

The system must enforce the following non-negotiable constraints, derived from operational requirements:

* **Aircraft-Gate Compatibility:** The assigned aircraft type (based on wingspan, MTOW, etc., defined in masterdata) must be compatible with the physical and weight capacity of the assigned gate.36  
* **Temporal Non-Overlap:** No two flights may be assigned to the same gate simultaneously. This includes ensuring clearance of the previous aircraft before the subsequent aircraft's projected arrival or pushback.37  
* **Buffer Requirements:** Mandatory, configurable time buffers must be incorporated both before arrival and after departure (e.g., 30 minutes minimum turn-around time, 15 minutes safety margin) to account for operational variability and potential towing requirements.36  
* **Assignment Stability:** To enhance predictability and passenger experience, the allocation logic must prioritize assigning flights to the same general terminal or pier.

##### **6.1.2. Optimization Approach**

The initial implementation of the resource assignment should employ a **greedy heuristic model** to solve the complex optimization problem.37 This involves iteratively assigning flights based on criteria (e.g., smallest aircraft first, or flights with the tightest time windows), minimizing conflicts and maximizing the value function (e.g., minimizing total passenger walking distance, a core objective).20

The architectural foundation, including PostgreSQL with pgvector, is crucial for the future evolution of this module. As operational data accumulates, the system can leverage vector analysis to build predictive allocation models, moving beyond simple greedy heuristics to sophisticated AI-driven optimization that forecasts resource demand and dynamically adapts assignments, further enhancing operational efficiency.9

#### **6.2. Check-in Counter Allocation Logic**

Check-in allocation must balance capacity with security and passenger flow optimization.

* **Assignment Stability:** The system must aim to keep a specific flight number assigned within the same check-in row across different operational days, contributing to improved passenger experience.20  
* **Passenger Flow Optimization (Minimize Walking Distance):** A key principle is that the allocated counter should provide the shortest possible walking distance to the departure gate. The allocation algorithm must take this geometric constraint into account.20  
* **Security Segregation:** The system must incorporate rigid security requirements for "high risk flights" (those with a government or security indication). The allocation plan must assign these flights to designated, isolated rows (e.g., Row 32\) and absolutely prohibit handling high-risk and non-high-risk flights simultaneously within the same row due to regulatory compliance.20

#### **6.3. Baggage Belt Allocation Logic**

Baggage belts must be managed against capacity and time limits during the arrival phase.

* **Time Window Management:** Each flight requires a belt assignment for a specific, limited duration (e.g., 60 minutes after landing). The system must track the requested start and end times for each assignment.38  
* **Capacity Constraints:** The core logic must implicitly satisfy the non-overlap requirement by processing flights based on arrival time and duration requests, ensuring that the cumulative assigned time does not exceed the belt’s maximum capacity within any given time horizon.21

### **7\. Module 4 & 5: Flight Information Display System (FIDS) and Social Media**

#### **7.1. FIDS Functional Requirements (fids app)**

The FIDS must operate as a highly reliable, real-time platform for disseminating information to passengers, ground handlers, and internal staff.15

##### **7.1.1. Display Content and Data Integrity**

The FIDS (A-FIDS and D-FIDS) must display critical, accurate data derived from the schedules and allocation apps:

* Airline identification (logo and IATA/ICAO designator).  
* City of origin and destination, including intermediate points.  
* Expected Arrival or Departure Time (capturing scheduled and real-time delays).  
* Gate number, Check-in counter numbers, and the corresponding airline/handling agent.39  
* Clear Flight Status (e.g., "Check-in Open," "Boarding," "Delayed," "Landed").39

##### **7.1.2. Configuration and Redundancy**

* **High Configuration Capacity:** The system must allow maximum configuration capability, supporting multiple display devices (LED, LCD/TFT) and manufacturers, each capable of showing unique screen layouts depending on their physical location (e.g., pre-security versus gate area).14  
* **Emergency Override:** A critical operational feature must allow manual system override to instantly change all or a subset of displays to show emergency information (e.g., fire alarm instructions or security alerts).22  
* **Revenue Integration:** The FIDS application must include a feature to dynamically rotate screens and incorporate targeted advertising and visual content (logos, video, news) to steer passenger traffic toward key concessionaires, thereby driving non-aeronautical revenue and integrating commercial objectives with operational delivery.22

##### **7.1.3. Technical Implementation (Channels)**

As previously established, the fids app leverages Django Channels and WebSockets to ensure real-time push capability.16 This requires ASGI consumers defined within the fids application that subscribe to changes in the flight data models. Any transaction affecting flight status or resource assignment must trigger a signal, which is processed by the Channels layer and pushed out as JSON data to all connected FIDS screens.18

#### **7.2. Social Media Module (social\_updates app)**

The social\_updates module enables the automated dissemination of critical operational changes to public platforms, enhancing communication and passenger engagement.

* **Secure Authentication:** The module must integrate a secure mechanism (such as python-social-auth) to manage and authenticate credentials for external platforms (e.g., Twitter/X, Facebook).28  
* **Update Triggering Pipeline:** Defined rules must exist to automatically publish pre-formatted flight messages when significant operational events occur (e.g., status changes to "Cancelled," or a Gate assignment change).  
* **User Interaction:** The system should provide an API or web interface allowing external users to "follow" specific flights, enabling personalized notifications via email, SMS, or direct social media response (roadmap item).40

### **8\. Module 6 & 7: Billing, BI, and External Systems Integration**

#### **8.1. Billing and Revenue Accounting Requirements (billing app)**

The billing module manages the airport’s financial relationship with airlines and handlers, ensuring accurate calculation of complex aeronautical and non-aeronautical fees.

##### **8.1.1. Core Aeronautical Revenue Engine**

The system must handle flexible contract, tariff, and discount management, automating revenue calculation based on complex metrics.41

* **Tariff Management:** Define detailed published tariffs, including standard fees and charges.  
* **Price-Influencing Factors:** The system must automatically apply surcharges and discounts based on operational data, including:  
  * Maximum Takeoff Weight (MTOW) of the aircraft.23  
  * Time of Operation (e.g., surcharges for night movements or public holidays, defined against established reportable hours).23  
  * Flight Service Usage: Accurate calculation based on the actual time the aircraft utilized airport services (e.g., actual flight time, fixed taxi time).42  
* **Contract Management:** Allows for the definition of special, negotiated contracts with individual airlines that override or modify standard published tariffs.23

##### **8.1.2. Invoicing and ERP Integration**

* **Invoice Generation:** Automate the calculation and generation of billing entries and invoices for credit customers based on freely definable periods (e.g., weekly, monthly).23  
* **Data Transfer:** The system must facilitate extensive integration with external Enterprise Resource Planning (ERP) systems to transfer calculated revenue data (including revenue code, customer identifier, currency, and exchange rate) for formal invoice printing and accounting ledger management.41

#### **8.2. External Integration (SITA Messaging) (integrations app)**

A fundamental requirement for interoperability within the aviation ecosystem is the ability to exchange standardized operational messages with airlines, ground handlers, and partners. This communication is typically handled via SITA (Société Internationale de Télécommunications Aéronautiques) messaging standards.43

* **SITA Type B Handling (Legacy):** The integrations app must incorporate logic to parse and generate Type B messages, which are fixed-format texts (maximum 60 lines of 63 characters).27 Examples include Movement (MVT) messages, which contain critical operational data such as Flight ID, aircraft registration, off-block time, and estimated takeoff time.27  
* **SITA Type X Handling (Modern):** The system must also support the modern Air Transport Industry Messaging Standard, Type X, which facilitates the exchange of larger messages with rich content (e.g., biometrics, aircraft performance) using XML formats.44 This requires robust XML processing capabilities to ensure compliance with current and future industry messaging protocols.

## **Conclusions and Recommendations**

The development of the Open Source Airport Management System (OS-AMS) in Django 5 is architecturally sound, provided that several high-leverage technical decisions are strictly adhered to. The analysis confirms that the system must adopt a **Modular Monolith architecture** across a minimum of nine specialized Django applications to manage domain complexity and facilitate maintainability.

The critical architectural requirements are centered around performance and integrity:

1. **Database Foundation:** The mandatory use of **PostgreSQL 16+ with TimescaleDB** is non-negotiable. TimescaleDB ensures the scalability and performance required for the voluminous, time-series data generated by operational and billing modules, directly supporting the financial viability of the system by guaranteeing rapid BI and revenue calculations.  
2. **Real-Time Capability:** The system must be deployed on an **ASGI stack using Django Channels** to fulfill the requirement for real-time FIDS updates, demanding a dedicated message broker infrastructure.  
3. **Open Source Strategy:** The choice of the **MIT License** coupled with a commitment to **Core Bootstrap** for the frontend maximizes commercial adoption and community contributions by removing proprietary licensing conflicts.  
4. **Domain Complexity:** The core challenge lies in the **Resource Allocation Engine** (Module 3\) and **External Integration** (Module 7). The allocation module must implement complex, constraint-based heuristics to handle compatibility, temporal non-overlap, security segregation, and passenger flow optimization. The integration module must handle fixed-format legacy standards (SSIM, Type B) with specialized parsers, isolating this complexity from the core business logic.

By adhering to this blueprint, the OS-AMS can provide small-to-medium airports with a highly scalable, modern, and cost-effective alternative to incumbent proprietary systems, enabling future growth in efficiency and analytical capabilities.

#### **Works cited**

1. The Art of Organizing Your Django Project: Apps vs. a Single Core App | Level 12, accessed November 19, 2025, [https://www.level12.io/blog/organizing-django-project-apps-single-app/](https://www.level12.io/blog/organizing-django-project-apps-single-app/)  
2. Building a Scalable and Maintainable Architecture for Large-Scale Django Projects, accessed November 19, 2025, [https://bluetickconsultants.medium.com/building-a-scalable-and-maintainable-architecture-for-large-scale-django-projects-78186b1caf8d](https://bluetickconsultants.medium.com/building-a-scalable-and-maintainable-architecture-for-large-scale-django-projects-78186b1caf8d)  
3. Django Best Practices: Projects vs. Apps | LearnDjango.com, accessed November 19, 2025, [https://learndjango.com/tutorials/django-best-practices-projects-vs-apps](https://learndjango.com/tutorials/django-best-practices-projects-vs-apps)  
4. PostgreSQL vs SQLite A Guide to Choosing the Right Database \- Boltic, accessed November 19, 2025, [https://www.boltic.io/blog/postgresql-vs-sqlite](https://www.boltic.io/blog/postgresql-vs-sqlite)  
5. SQLite vs PostgreSQL: A Detailed Comparison \- DataCamp, accessed November 19, 2025, [https://www.datacamp.com/blog/sqlite-vs-postgresql-detailed-comparison](https://www.datacamp.com/blog/sqlite-vs-postgresql-detailed-comparison)  
6. TimeScaleDB App — Django App: RealTimeDB documentation, accessed November 19, 2025, [https://timescaledb-app.readthedocs.io/](https://timescaledb-app.readthedocs.io/)  
7. Building Multi-Node Django Systems for Time-Series Data \[Free Course\], accessed November 19, 2025, [https://www.tigerdata.com/blog/building-multi-node-django-systems-for-time-series-data-free-course](https://www.tigerdata.com/blog/building-multi-node-django-systems-for-time-series-data-free-course)  
8. Using PGvector with your Django App \- DEV Community, accessed November 19, 2025, [https://dev.to/buddhiraz/using-pgvector-with-your-django-app-2o3j](https://dev.to/buddhiraz/using-pgvector-with-your-django-app-2o3j)  
9. Mastering the Skies: Strategic Resource Allocation for Aviation Success \- KanBo, accessed November 19, 2025, [https://kanboapp.com/en/industries/aviation/mastering-the-skies-strategic-resource-allocation-for-aviation-success/](https://kanboapp.com/en/industries/aviation/mastering-the-skies-strategic-resource-allocation-for-aviation-success/)  
10. Django \+ Pgvector \+ LLMs \= Semantic Search and AI Agent Powered Document Analytics \- Reddit, accessed November 19, 2025, [https://www.reddit.com/r/django/comments/1dn1exe/django\_pgvector\_llms\_semantic\_search\_and\_ai\_agent/](https://www.reddit.com/r/django/comments/1dn1exe/django_pgvector_llms_semantic_search_and_ai_agent/)  
11. Twitter Bootstrap Vs Themeforest Admin Themes \- Stack Overflow, accessed November 19, 2025, [https://stackoverflow.com/questions/10065646/twitter-bootstrap-vs-themeforest-admin-themes](https://stackoverflow.com/questions/10065646/twitter-bootstrap-vs-themeforest-admin-themes)  
12. MIT License \- Wikipedia, accessed November 19, 2025, [https://en.wikipedia.org/wiki/MIT\_License](https://en.wikipedia.org/wiki/MIT_License)  
13. Should I learn Bootstrap to be a Django web developer? \- Quora, accessed November 19, 2025, [https://www.quora.com/Should-I-learn-Bootstrap-to-be-a-Django-web-developer](https://www.quora.com/Should-I-learn-Bootstrap-to-be-a-Django-web-developer)  
14. FLIGHT INFORMATION DISPLAY SYSTEM \- Indra, accessed November 19, 2025, [https://www.indracompany.com/sites/default/files/as\_fids.pdf](https://www.indracompany.com/sites/default/files/as_fids.pdf)  
15. A Practical Guide \- Airport Flight Information Systems, accessed November 19, 2025, [https://blog.airport-information-systems.com/airport-flight-information-systems-guide-with-checklist/](https://blog.airport-information-systems.com/airport-flight-information-systems-guide-with-checklist/)  
16. Tutorial — Channels 4.3.1 documentation, accessed November 19, 2025, [https://channels.readthedocs.io/en/latest/tutorial/](https://channels.readthedocs.io/en/latest/tutorial/)  
17. Tutorial Part 1: Basic Setup \- Django Channels, accessed November 19, 2025, [https://channels.readthedocs.io/en/stable/tutorial/part\_1.html](https://channels.readthedocs.io/en/stable/tutorial/part_1.html)  
18. WebSocket in Django \- DEV Community, accessed November 19, 2025, [https://dev.to/foxy4096/websocket-in-django-55p1](https://dev.to/foxy4096/websocket-in-django-55p1)  
19. aerops.ground Airport Management System (AMS), accessed November 19, 2025, [https://www.aerops.com/en/flughaefen-fbo/airport-management-system-ams/](https://www.aerops.com/en/flughaefen-fbo/airport-management-system-ams/)  
20. Check-In Desk Allocation Regulation Schiphol, accessed November 19, 2025, [https://www.schiphol.nl/en/download/b2b/1554102594/2rkoHuvFzu4g82OaesC22Y.pdf](https://www.schiphol.nl/en/download/b2b/1554102594/2rkoHuvFzu4g82OaesC22Y.pdf)  
21. The Baggage Belt Assignment Problem, accessed November 19, 2025, [https://backend.orbit.dtu.dk/ws/portalfiles/portal/258648014/Melju\_1\_s2.0\_S2192437621000133\_main.pdf](https://backend.orbit.dtu.dk/ws/portalfiles/portal/258648014/Melju_1_s2.0_S2192437621000133_main.pdf)  
22. Flight Information Display Systems \- Collins Aerospace, accessed November 19, 2025, [https://www.collinsaerospace.com/what-we-do/industries/airports/airport-operations/flight-information-display-systems](https://www.collinsaerospace.com/what-we-do/industries/airports/airport-operations/flight-information-display-systems)  
23. Airport Contract & Billing Systems by A-ICE | Airport Operations Streamlining, accessed November 19, 2025, [https://www.airport-operations.com/contract-billing](https://www.airport-operations.com/contract-billing)  
24. Key Performance Indicators (KPIs) for Small Airport Management \- CRP, accessed November 19, 2025, [https://crp.trb.org/acrpwebresource6/wp-content/uploads/sites/13/2018/02/KPIs-for-Small-Airports.docx](https://crp.trb.org/acrpwebresource6/wp-content/uploads/sites/13/2018/02/KPIs-for-Small-Airports.docx)  
25. Prepare Effective Dashboard \- Airport and Aviation consultant, Financial planning, accessed November 19, 2025, [https://dwuconsulting.com/tools/articles/prepare-effective-dashboard](https://dwuconsulting.com/tools/articles/prepare-effective-dashboard)  
26. Flight Schedules From SSIM \- Octallium, accessed November 19, 2025, [https://www.octallium.com/blog/2025/02/27/flight-schedules-from-ssim/](https://www.octallium.com/blog/2025/02/27/flight-schedules-from-ssim/)  
27. Type B Messaging \- IATA, accessed November 19, 2025, [https://www.iata.org/contentassets/badbfd2d36a74f12b021c9dd899ecbad/type\_b\_messaging\_whitepaper\_v2dot1\_14\_june\_2024.pdf](https://www.iata.org/contentassets/badbfd2d36a74f12b021c9dd899ecbad/type_b_messaging_whitepaper_v2dot1_14_june_2024.pdf)  
28. Django Framework \- Python Social Auth, accessed November 19, 2025, [https://python-social-auth.readthedocs.io/en/latest/configuration/django.html](https://python-social-auth.readthedocs.io/en/latest/configuration/django.html)  
29. OPINION: Optimizing Local Airports for Advanced Air Mobility \- KinectAir, accessed November 19, 2025, [https://www.kinectair.com/post/opinion-optimizing-local-airports-for-advanced-air-mobility](https://www.kinectair.com/post/opinion-optimizing-local-airports-for-advanced-air-mobility)  
30. Stand-Allocation System (SAS): A Constraint-Based System Developed with Software Components. \- ResearchGate, accessed November 19, 2025, [https://www.researchgate.net/publication/220604512\_Stand-Allocation\_System\_SAS\_A\_Constraint-Based\_System\_Developed\_with\_Software\_Components](https://www.researchgate.net/publication/220604512_Stand-Allocation_System_SAS_A_Constraint-Based_System_Developed_with_Software_Components)  
31. MIT Licenses Explained \- Wiz, accessed November 19, 2025, [https://www.wiz.io/academy/mit-licenses-explained](https://www.wiz.io/academy/mit-licenses-explained)  
32. jahnvisahni31/Airport\_analysis: This project is a comprehensive Power BI dashboard analyzing airport operations, focusing on flight delays, time analysis, and detailed flight information to improve efficiency and passenger satisfaction. \- GitHub, accessed November 19, 2025, [https://github.com/jahnvisahni31/Airport\_analysis](https://github.com/jahnvisahni31/Airport_analysis)  
33. KPI OVERVIEW \- GANP Portal \- ICAO Secure Login, accessed November 19, 2025, [https://www4.icao.int/ganpportal/ASBU/KPI](https://www4.icao.int/ganpportal/ASBU/KPI)  
34. ASPM Efficiency: Reportable Hours by Facility Report \- FAA Operations & Performance Data, accessed November 19, 2025, [https://www.aspm.faa.gov/aspmhelp/index/ASPM\_Efficiency\_\_Reportable\_Hours\_by\_Facility\_Report.html](https://www.aspm.faa.gov/aspmhelp/index/ASPM_Efficiency__Reportable_Hours_by_Facility_Report.html)  
35. Standard Schedules Information Manual (SSIM) \- IATA, accessed November 19, 2025, [https://www.iata.org/en/publications/manuals/standard-schedules-information/](https://www.iata.org/en/publications/manuals/standard-schedules-information/)  
36. Optimizing Airport Gate Assignments: Methods & Metrics | BQP, accessed November 19, 2025, [https://www.bqpsim.com/blogs/airport-gate-optimization](https://www.bqpsim.com/blogs/airport-gate-optimization)  
37. The Airport Gate Assignment Problem: A Survey \- PMC \- NIH, accessed November 19, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC4258332/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4258332/)  
38. Baggage Carousel Etiquette: 5 Top Tips \- Simple Flying, accessed November 19, 2025, [https://simpleflying.com/baggage-carousel-etiquette-5-top-tips/](https://simpleflying.com/baggage-carousel-etiquette-5-top-tips/)  
39. The Best Information to Display On Airport Screens During the Transit Process \- Mvix, accessed November 19, 2025, [https://www.mvix.com/blog/what-to-display-on-your-airport-screens](https://www.mvix.com/blog/what-to-display-on-your-airport-screens)  
40. Flights API Integration Guide 2025 | Booking & Pricing \- phptravels, accessed November 19, 2025, [https://phptravels.com/blog/comprehensive-guide-to-flights-api-integration](https://phptravels.com/blog/comprehensive-guide-to-flights-api-integration)  
41. Airport Billing \- Airport Technology, accessed November 19, 2025, [https://www.airport-technology.com/products/airport-billing/](https://www.airport-technology.com/products/airport-billing/)  
42. Estimated vs. Actual Flight Time in Private Aviation Billing | Magellan Jets, accessed November 19, 2025, [https://magellanjets.com/library/insights/estimated-vs-actual-flight-time-in-private-aviation-billing/](https://magellanjets.com/library/insights/estimated-vs-actual-flight-time-in-private-aviation-billing/)  
43. SITA Airport Management, accessed November 19, 2025, [https://www.sita.aero/solutions/sita-at-airports/sita-operations-at-airports/sita-airport-management/](https://www.sita.aero/solutions/sita-at-airports/sita-operations-at-airports/sita-airport-management/)  
44. SITA Messaging, accessed November 19, 2025, [https://www.sita.aero/solutions/sita-communications-and-data-exchange/sita-messaging/](https://www.sita.aero/solutions/sita-communications-and-data-exchange/sita-messaging/)
