# ✈️ OS-AMS: Open Source Airport Management System

![License](https://img.shields.io/badge/license-Open%20Source-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)

## 📋 Project Overview

**OS-AMS** is a modular, high-performance Airport Management System designed to replace expensive legacy infrastructure for Small-to-Medium Airports (SMAs). Built with modern technologies, it provides a comprehensive solution for managing critical airport operations.

### Key Features

- 🛫 **Flight Scheduling** - Seasonal and daily flight plan management (SSIM import support)
- 🚪 **Resource Allocation** - Intelligent constraint-based gate and check-in counter assignment
- 📺 **FIDS** - Real-time Flight Information Display System (WebSocket-driven)
- 💰 **Aeronautical Billing** - Automated fee calculation (landing, parking, passenger)
- 📊 **BI Analytics** - Comprehensive dashboards with time-series analytics
- 🎨 **Modern UI** - Responsive Bootstrap 5 interface with light/dark theme support
- 🔐 **Authentication** - Secure user login and role-based access control

## 🚀 Technology Stack

### Backend

- **Framework:** Django 5.2
- **Language:** Python 3.12
- **Architecture:** Modular Monolith
- **API:** REST (planned: Django REST Framework)

### Database

- **Primary:** TimescaleDB (PostgreSQL 16-based)
  - Optimized for time-series flight tracking and resource utilization logs
- **Cache:** Redis (for Celery task queue and Django Channels)

### Frontend

- **Framework:** Bootstrap 5
- **Icons:** Bootstrap Icons
- **Charts:** Chart.js
- **Real-time:** HTMX + Django Channels (WebSockets)
- **Theme:** Custom light/dark mode

### DevOps

- **Containerization:** Docker & Docker Compose
- **Database:** TimescaleDB container
- **Web Server:** Gunicorn (production)
- **Development:** Django Development Server

## 📁 Project Structure

```bash
osams/
├── core_app/                 # Main application
│   ├── views.py             # Authentication & dashboard views
│   ├── models.py            # Database models
│   └── admin.py             # Django admin configuration
├── os_ams/                  # Project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── templates/               # HTML templates
│   ├── base.html            # Main layout with sidebar
│   ├── base-minimal.html    # Minimal layout (login)
│   ├── login.html           # Login page
│   ├── index.html           # Dashboard
│   └── sidebar.html         # Navigation sidebar
├── static/                  # Static assets
│   ├── css/style.css        # Custom styles
│   ├── js/script.js         # JavaScript
│   └── img/logo.png         # Application logo
├── devops/                  # DevOps scripts
├── artefacts/               # Documentation & design
│   ├── prd.md              # Product Requirements Document
│   └── aims.md             # Project aims
├── docker-compose.yml       # Docker services
├── Dockerfile               # Application container
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
└── .env                    # Environment variables
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git
- WSL2 (if on Windows)

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/Iotonix/osams.git
   cd osams
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the database**

   ```bash
   docker-compose up -d timescaledb
   ```

4. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**

   ```bash
   ./create_superuser.sh
   # Or manually:
   # python manage.py createsuperuser
   ```

7. **Start the development server**

   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Login: <http://localhost:8000/login/>
   - Dashboard: <http://localhost:8000/>
   - Admin: <http://localhost:8000/admin/>

### Default Credentials

After running `create_superuser.sh`:

- **Username:** admin
- **Password:** admin123
- **Email:** <ralf.hundertmark@yahoo.com>

## 🐳 Docker Deployment

### Build the image

```bash
./build_manually.sh
```

### Run with Docker Compose

```bash
docker-compose up -d
```

## 🗄️ Database Configuration

The system uses **TimescaleDB** for optimized time-series data handling:

- **Database:** osams
- **User:** pgadmin
- **Password:** pgosams123 (change in production!)
- **Port:** 5432
- **Host:** localhost (development) / timescaledb (Docker)

Configuration is managed via `.env` file:

```env
POSTGRES_DB=osams
POSTGRES_USER=pgadmin
POSTGRES_PASSWORD=pgosams123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## 🎨 UI Themes

OS-AMS features a modern dual-theme interface:

- **Light Theme:** Clean, professional daytime interface
- **Dark Theme:** Eye-friendly night operations mode
- **Sidebar:** Always dark for consistent navigation
- **Theme Toggle:** Top-right corner (persistent via localStorage)

## 🎨 UI Design Philosophy

OS-AMS uses a **full-page form approach** (no modals) for better user experience:

- **List Views:** Clean table layouts with search functionality and inline actions
- **Add/Edit Forms:** Full-page forms with Bootstrap styling for clarity and accessibility
- **Consistent UX:** All master data follows the same pattern: List → Add/Edit → Back to List
- **Responsive Design:** Forms and tables adapt seamlessly to different screen sizes

## 📦 Core Modules

### ✅ Master Data (Implemented)

The **masterdata** module provides comprehensive management of airport reference data:

#### Aviation Data

- **Airlines** - Carrier profiles with IATA/ICAO codes, contact info, and ground handler assignments
- **Airports** - Global airport reference data (origin/destination for routes)
- **Aircraft Types** - Aircraft specifications including wingspan, capacity, wake turbulence category
- **Routes** - Airline route configurations between airports with equipment info

#### Airport Infrastructure

- **Terminals** - Terminal buildings configuration
- **Gates** - Boarding gates with type (contact/remote), capacity, and availability tracking
- **Stands** - Aircraft parking stands/aprons with size codes and pushback requirements
- **Check-in Counters** - Check-in desk allocation and grouping
- **Baggage Carousels** - Baggage claim belt configuration
- **Runways** - Runway specifications including dimensions and surface type
- **Ground Handlers** - Ground handling agents with service capabilities

All master data entities support:

- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Search and filtering
- ✅ Soft delete (is_active flag)
- ✅ Audit trails (created_at, updated_at timestamps)
- ✅ Bootstrap 5 styled forms and tables

### ✅ Schedules (Implemented)

The **schedules** module manages seasonal flight schedules:

- **Seasonal Flights** - Template-based flight schedules with:
  - Airline, flight number, route (origin/destination)
  - Aircraft type and schedule times (STD/STA)
  - Season dates (start/end) and days of operation
  - Active/inactive status for planning flexibility
- **Seeding Command** - Generate 1,200+ seasonal flights from route data with intelligent frequency distribution
- **Full CRUD** - Add, edit, delete seasonal flight templates

### ✅ Flight Operations (Implemented)

The **flight_ops** module handles daily flight operations with advanced features:

- **Daily Flights** - Concrete flight instances with:
  - Complete timeline tracking (scheduled, estimated, actual times for departure/arrival)
  - Resource allocation (gates, stands, check-in counters, baggage carousels)
  - Flight status management (scheduled, boarding, departed, arrived, cancelled, etc.)
  - Manual modification tracking for operational changes
  - Public remarks and QR code data

- **Rolling Window Strategy** - Template & Instance pattern:
  - **Seasonal Flights** = "Perfect Plan" (templates)
  - **Daily Flights** = "Concrete Reality" (instances)
  - Auto-generate 90-day advance window from templates
  - Smart propagation respects manual modifications (dirty flag pattern)
  - 48-hour buffer before auto-updates to protect near-term ops

- **Management Commands:**
  - `generate_daily_flights` - Create daily instances from seasonal templates (90-day rolling window)
  - `propagate_schedule_changes` - Sync template changes to future flights (respects manual edits)

- **Performance Optimizations:**
  - **Django-Select2** - AJAX autocomplete for airlines/airports (0.4s load time vs 5s)
  - Query caching (5-minute cache for frequently used IDs)
  - Date-based pagination (~880 flights/day instead of 78K total)
  - Logging for performance monitoring

- **Data Volume:** Currently managing 78,380 daily flight records across 94 airlines and 122 airports

### 🚧 Operational Modules (Planned)

1. **allocation** - Constraint-based gate and check-in assignment engine
2. **fids** - Real-time Flight Information Display System (WebSocket-driven)
3. **billing** - Aeronautical fee calculation
4. **bi_stats** - Analytics dashboards using TimescaleDB hyper-functions

## 🔧 Development

### Running Tests

```bash
python manage.py test
```

### Code Style

```bash
# Format code
black .

# Linting
flake8 .
```

### Database Shell

```bash
# Django shell
python manage.py shell

# PostgreSQL shell
psql -h localhost -U pgadmin -d osams
```

## 📚 Documentation

- [Product Requirements Document](artefacts/prd.md)
- [Project Aims](artefacts/aims.md)
- API Documentation (coming soon)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source. See LICENSE file for details.

## 👥 Team

- **Developer:** Ralf Hundertmark
- **Organization:** Iotonix

## 🐛 Known Issues

- Celery worker integration pending
- Redis cache configuration pending
- Django Channels for WebSocket support pending
- Resource allocation algorithm to be implemented
- SSIM import functionality pending

## 📮 Contact

For questions or support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for the aviation industry**
