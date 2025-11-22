# 🚀 OS-AMS Implementation Plan

**Project:** Open Source Airport Management System  
**Version:** 1.0  
**Last Updated:** November 22, 2025  
**Status:** Phase 1 - Foundation

---

## 📋 Executive Summary

OS-AMS will be developed in iterative phases, starting with core master data management and gradually building out operational modules. The initial focus is on creating a solid foundation with Django Admin for rapid prototyping, followed by custom UI development as the system matures.

**Key Decisions:**

- ✅ Django Admin for all CRUD operations (Phase 1-2)
- ✅ Custom UI considered for Phase 3+ (separate admin project)
- ✅ REST API development deferred to later phases
- ✅ Focus on internal operations, not AODB integration initially
- ✅ Accordion-style sidebar with collapsible sub-menus

---

## 🏗️ Architecture Overview

### Application Structure

```
osams/
├── core_app/              # Authentication, dashboard, shared utilities
├── masterdata/            # Airlines, aircraft, gates, terminals, infrastructure
├── flight_ops/            # Daily operations, turnarounds, delays, disruptions
├── flight_planning/       # Schedule management, SSIM import, seasonal planning
├── resource_mgmt/         # Gate allocation, check-in counter assignment
├── fids/                  # Flight Information Display System
├── billing/               # Aeronautical charges, invoicing, rate cards
└── analytics/             # BI dashboards, reports, performance metrics
```

### Technology Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Admin Interface** | Django Admin | Rapid development, built-in CRUD, sufficient for Phase 1-2 |
| **Database** | TimescaleDB (PG16) | Time-series optimization for flight tracking |
| **Cache/Queue** | Redis | Celery task queue, Django Channels (future) |
| **Frontend** | Bootstrap 5 + HTMX | Responsive, modern, minimal JS complexity |
| **API** | Deferred to Phase 3+ | Focus on core functionality first |
| **Real-time** | Django Channels | WebSocket support for FIDS (Phase 2) |

---

## 📅 Implementation Phases

### **Phase 1: Foundation & Master Data** (Weeks 1-3)

**Goal:** Establish core infrastructure and master data management

#### Week 1: Setup & Structure

- [x] Initial project setup with Django 5.2
- [x] TimescaleDB configuration
- [x] Docker Compose setup
- [x] Authentication system with login page
- [x] Base UI templates (light/dark theme)
- [ ] Create all Django apps structure
- [ ] Configure Django Admin for all apps
- [ ] Implement collapsible sidebar navigation

#### Week 2: Master Data Models

**masterdata app:**

- [ ] **Airlines Model**
  - IATA code (3-letter), ICAO code (3-letter)
  - Name, logo, contact information
  - Active status, created/modified timestamps
  
- [ ] **Aircraft Types Model**
  - ICAO code, IATA code, manufacturer, model name
  - Capacity (pax), wingspan, weight class (A-F)
  - Wake turbulence category
  
- [ ] **Terminals Model**
  - Code, name, type (domestic/international)
  - Capacity, operating hours
  
- [ ] **Gates Model**
  - Gate number, terminal reference
  - Type (contact/remote), status (active/maintenance)
  - Aircraft type restrictions (many-to-many)
  - Jetbridge availability
  
- [ ] **Stands/Aprons Model**
  - Stand code, location, size category
  - Aircraft compatibility, utilities available
  
- [ ] **Check-in Counters Model**
  - Counter range (e.g., 101-110), terminal
  - Counter group, availability status
  
- [ ] **Baggage Carousels Model**
  - Carousel number, terminal, status

#### Week 3: Admin Configuration & Data

- [ ] Customize Django Admin interfaces (list_display, filters, search)
- [ ] Add inline editing for related models (Gates → Terminal)
- [ ] Create data import management commands (CSV bulk import)
- [ ] Seed initial demo data (sample airlines, gates, aircraft)
- [ ] Add data validation and constraints
- [ ] Implement audit trail (created_by, modified_by fields)

**Deliverables:**

- ✅ Functional master data management via Django Admin
- ✅ Complete sidebar navigation (mockup ready)
- ✅ Sample data for demo purposes
- ✅ Basic dashboard showing data counts

---

### **Phase 2: Flight Planning & Operations** (Weeks 4-7)

**Goal:** Enable flight schedule management and daily operations

#### flight_planning app

- [ ] **Flight Schedule Model** (Seasonal)
  - Flight number, airline, route (origin/destination)
  - Days of operation (bit flags: Mon-Sun)
  - Scheduled times (STD/STA), aircraft type
  - Effective dates (valid from/until)
  
- [ ] **SSIM Import** functionality
  - Parse SSIM standard format files
  - Validate against master data
  - Bulk schedule creation
  
- [ ] **Schedule Browser UI**
  - Filter by airline, date range, route
  - Edit/delete schedules
  - Conflict detection (double bookings)

#### flight_ops app

- [ ] **Daily Flight Model** (Operational)
  - Reference to flight schedule
  - Actual times (ATD/ATA), delays
  - Status (scheduled/boarding/departed/arrived/cancelled)
  - Gate assignment, stand assignment
  - Check-in counters, baggage carousel
  
- [ ] **Live Operations Dashboard**
  - Today's flight list (departures/arrivals)
  - Status indicators, delay visualization
  - Quick actions (change gate, mark delay)
  
- [ ] **Turnaround Monitor**
  - Show aircraft on ground
  - Inbound/outbound flight pairing
  - Ground time calculation

**Deliverables:**

- ✅ Flight schedule management
- ✅ Daily operational flight tracking
- ✅ Live dashboard showing today's operations
- ✅ SSIM import capability

---

### **Phase 3: Resource Allocation Engine** (Weeks 8-10)

**Goal:** Automated and manual resource assignment

#### resource_mgmt app

- [ ] **Gate Allocation Algorithm**
  - Constraint satisfaction: aircraft type compatibility, terminal preferences
  - Time-based conflict prevention
  - Optimization: minimize walking distance, balance terminal load
  - Manual override capability
  
- [ ] **Check-in Allocation**
  - Assign counter groups to flights
  - Open/close times based on flight schedule
  - Airline preferences
  
- [ ] **Allocation Dashboard**
  - Visual timeline (Gantt chart) of gate usage
  - Drag-and-drop reassignment
  - Conflict warnings
  
- [ ] **Stand Management**
  - Remote stand assignment for overflow
  - Bus allocation tracking

**Deliverables:**

- ✅ Automated gate allocation with manual overrides
- ✅ Check-in counter management
- ✅ Resource utilization visualization
- ✅ Conflict detection and resolution

---

### **Phase 4: FIDS & Real-time Updates** (Weeks 11-13)

**Goal:** Flight Information Display System with live updates

#### fids app

- [ ] **Django Channels Setup**
  - WebSocket consumer for flight updates
  - Redis channel layer configuration
  
- [ ] **Display Templates**
  - Departures board (filterable by terminal)
  - Arrivals board
  - Gate-specific displays
  - Baggage claim displays
  
- [ ] **FIDS Admin**
  - Configure display screens (URL parameters)
  - Update refresh intervals
  - Emergency message broadcasting
  
- [ ] **Real-time Push**
  - Flight status changes → WebSocket push
  - Automatic board updates (no page reload)

**Deliverables:**

- ✅ Live departures/arrivals boards
- ✅ WebSocket-based real-time updates
- ✅ Configurable display screens
- ✅ Emergency messaging system

---

### **Phase 5: Billing & Invoicing** (Weeks 14-16)

**Goal:** Aeronautical charge calculation and invoicing

#### billing app

- [ ] **Rate Cards Model**
  - Landing fees (by MTOW), parking fees (per hour/block)
  - Passenger fees, lighting fees
  - Effective date ranges, airline-specific rates
  
- [ ] **Charge Calculation Engine**
  - Automatic calculation on flight completion
  - Weight-based, time-based, passenger-based formulas
  - Special rate handling (cargo flights, training flights)
  
- [ ] **Invoice Generation**
  - Group charges by airline, billing period
  - PDF invoice generation
  - Export to accounting systems (CSV/Excel)
  
- [ ] **Billing Dashboard**
  - Revenue overview, unbilled charges
  - Airline account statements

**Deliverables:**

- ✅ Automated charge calculation
- ✅ Invoice generation and export
- ✅ Revenue reporting dashboard

---

### **Phase 6: Analytics & Reporting** (Weeks 17-19)

**Goal:** Business intelligence and performance metrics

#### analytics app

- [ ] **Performance Dashboards**
  - On-time performance (OTP) metrics
  - Gate utilization rates
  - Peak hour analysis
  - Airline performance rankings
  
- [ ] **TimescaleDB Hyper-functions**
  - Time-bucket aggregations
  - Continuous aggregates for historical data
  - Real-time analytics queries
  
- [ ] **Report Generation**
  - Scheduled reports (daily/weekly/monthly)
  - Custom report builder
  - Export capabilities (PDF, Excel, CSV)
  
- [ ] **Visualizations**
  - Chart.js integration
  - Interactive time-series graphs
  - Heatmaps (busy times, popular routes)

**Deliverables:**

- ✅ Comprehensive analytics dashboard
- ✅ Automated report generation
- ✅ Historical trend analysis
- ✅ Performance KPIs

---

## 🎯 Current Sprint (Phase 1, Week 1)

### Immediate Tasks (Next 24-48 Hours)

#### ✅ Completed

- [x] Project setup and configuration
- [x] Docker Compose with TimescaleDB
- [x] Authentication system and login page
- [x] Base templates with theme support
- [x] README documentation

#### 🚧 In Progress

- [ ] **Create Django Apps** (30 min)

  ```bash
  python manage.py startapp masterdata
  python manage.py startapp flight_ops
  python manage.py startapp flight_planning
  python manage.py startapp resource_mgmt
  python manage.py startapp fids
  python manage.py startapp billing
  python manage.py startapp analytics
  ```
  
- [ ] **Build Sidebar Navigation** (2 hours)
  - Implement accordion-style collapsible menu
  - Add all main sections with sub-menus
  - Icons for each section (Bootstrap Icons)
  - Active state highlighting
  - Smooth animations
  - Responsive mobile behavior

- [ ] **Update Dashboard** (30 min)
  - Add welcome message with user name
  - Placeholder cards for future metrics
  - Quick action buttons

#### 📋 Next Tasks (After Demo)

- [ ] Design master data models
- [ ] Configure Django Admin
- [ ] Create initial migrations
- [ ] Add sample data fixtures

---

## 🎨 UI/UX Guidelines

### Sidebar Menu Structure

```
📊 Dashboard                     [Home icon, always expanded]

📂 Master Data                   [Collapsible]
   ├── Airlines
   ├── Aircraft Types
   ├── Gates & Terminals
   ├── Stands & Aprons
   └── Infrastructure

✈️ Flight Operations            [Collapsible]
   ├── Live Status
   ├── Turnaround Monitor
   └── Delays & Disruptions

📅 Flight Planning              [Collapsible]
   ├── Schedule Browser
   ├── Import SSIM
   └── Seasonal Planning

🎯 Resource Management          [Collapsible]
   ├── Gate Allocation
   ├── Check-in Assignment
   └── Stand Management

📺 FIDS                         [Collapsible]
   ├── Departures Board
   ├── Arrivals Board
   └── Display Configuration

💰 Billing                      [Collapsible]
   ├── Charge Calculation
   ├── Invoices
   └── Rate Cards

📈 Analytics                    [Collapsible]
   ├── Operations Dashboard
   ├── Performance Reports
   └── Historical Analysis

⚙️ Settings                     [Bottom, gear icon]
```

### Design Principles

- **Consistency:** Same icon style, spacing, colors throughout
- **Clarity:** Clear labels, no jargon without explanation
- **Efficiency:** Most-used features prominently placed
- **Feedback:** Visual confirmation of actions (toasts, highlights)
- **Accessibility:** Keyboard navigation, screen reader support

---

## 🔐 Security & Permissions (Future)

### User Roles (Phase 2+)

| Role | Permissions |
|------|-------------|
| **Operations Staff** | View flight ops, FIDS; Read-only master data |
| **Flight Planners** | Edit schedules, planning; Read-only ops |
| **Resource Managers** | Gate/counter allocation; Edit resource data |
| **Finance** | Full billing access; Read-only operations |
| **Administrators** | Full system access, user management |

### Implementation

- Django's built-in permissions system
- Group-based access control
- Model-level permissions (add/change/delete/view)
- Custom permissions for specific actions (e.g., "can_override_allocation")

---

## 📊 Success Metrics

### Phase 1 KPIs

- ✅ All master data entities modeled
- ✅ 100+ sample records across entities
- ✅ Django Admin fully configured
- ✅ Sidebar navigation complete and functional
- ✅ Demo-ready in 48 hours

### Phase 2 KPIs

- ✅ 1000+ flights schedulable
- ✅ SSIM import processing < 5 seconds for 100 flights
- ✅ Real-time operations dashboard updates

### Phase 3+ KPIs

- ✅ Gate allocation algorithm < 2 seconds for daily schedule
- ✅ 95%+ optimal gate assignments
- ✅ FIDS update latency < 500ms
- ✅ Invoice generation < 10 seconds

---

## 🚫 Out of Scope (Current Phases)

**Deferred to Future Versions:**

- ❌ REST API for external integrations
- ❌ AODB (Airport Operational Database) connectivity
- ❌ SITA/ARINC message integration
- ❌ Mobile applications
- ❌ Multi-airport support (single airport focus initially)
- ❌ Integration with A-CDM systems
- ❌ Passenger processing (check-in, boarding)
- ❌ Baggage tracking system integration
- ❌ Weather integration
- ❌ NOTAMs management

**These features will be considered after:**

- Core functionality is stable
- User feedback collected
- Community contributors identified
- External funding/support secured

---

## 🤝 Contribution Strategy (Future)

### Phase 3+ Open Source Readiness

1. **Documentation:** Comprehensive API docs, contribution guidelines
2. **Testing:** 80%+ code coverage, CI/CD pipeline
3. **Licensing:** Clear open-source license (MIT/Apache 2.0)
4. **Community:** GitHub issues, discussions, roadmap visibility
5. **Modularity:** Plugins/extensions architecture for custom features

### Target Contributors

- Airport IT departments
- Aviation software developers
- University/research projects
- Open-source enthusiasts

---

## 📝 Notes & Decisions Log

### November 22, 2025

- **Decision:** Use Django Admin for Phase 1-2 CRUD operations
  - *Rationale:* Faster development, proven reliability, sufficient for internal use
  - *Future:* Custom UI as separate "admin project" if needed
  
- **Decision:** REST API deferred to Phase 3+
  - *Rationale:* Focus on core functionality, not all data should be exposed
  - *Future:* API design once operational requirements are clear
  
- **Decision:** Accordion-style sidebar navigation
  - *Rationale:* Clean, organized, supports many menu items without clutter
  - *Alternative considered:* Flyout menus (rejected: less mobile-friendly)

- **Decision:** TimescaleDB on PostgreSQL 16 (not 17)
  - *Rationale:* Client compatibility issues with PG17, stable PG16 ecosystem
  
- **Decision:** Build sidebar completely first, connect functionality later
  - *Rationale:* Demo-ready mockup needed for pitch/presentation

---

## 📞 Contact & Support

**Project Lead:** Ralf Hundertmark  
**Organization:** Iotonix  
**Repository:** <https://github.com/Iotonix/osams>  

For questions, suggestions, or collaboration inquiries, please open a GitHub issue or contact the project maintainer.

---

**Last Updated:** November 22, 2025  
**Next Review:** December 1, 2025 (End of Phase 1, Week 1)
