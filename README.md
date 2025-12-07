# **✈️ OS-AMS: Open Source Airport Management System**

## **📋 Project Overview**

**OS-AMS** is a modular, high-performance Airport Management System designed to replace expensive legacy infrastructure for Small-to-Medium Airports (SMAs). Built with modern technologies, it provides a comprehensive solution for managing critical airport operations.

### **Key Features**

* 🛫 **Flight Scheduling** \- Seasonal and daily flight plan management (SSIM import support)  
* 📊 **Visual Operations** \- **\[NEW\]** Interactive Gantt charts for resource timeline visualization  
* 🚪 **Resource Allocation** \- Intelligent constraint-based gate and check-in counter assignment  
* 📺 **FIDS** \- Real-time Flight Information Display System (WebSocket-driven)  
* 💰 **Aeronautical Billing** \- Automated fee calculation (landing, parking, passenger)  
* 📈 **BI Analytics** \- Comprehensive dashboards with time-series analytics  
* 🎨 **Modern UI** \- Responsive Bootstrap 5 interface with light/dark theme support  
* 🔐 **Authentication** \- Secure user login and role-based access control

## **🚀 Technology Stack**

### **Backend**

* **Framework:** Django 5.2  
* **Language:** Python 3.12  
* **Architecture:** Modular Monolith  
* **API:** REST (planned: Django REST Framework)

### **Database**

* **Primary:** TimescaleDB (PostgreSQL 16-based)  
  * Optimized for time-series flight tracking and resource utilization logs  
* **Cache:** Redis (for Celery task queue and Django Channels)

### **Frontend**

* **Framework:** Bootstrap 5  
* **Icons:** Bootstrap Icons  
* **Visualization:** Vis.js (Timelines), Chart.js  
* **Real-time:** HTMX \+ Django Channels (WebSockets)  
* **Theme:** Custom light/dark mode

### **DevOps**

* **Containerization:** Docker & Docker Compose  
* **Database:** TimescaleDB container  
* **Web Server:** Gunicorn (production)  
* **Development:** Django Development Server

## **📁 Project Structure**

osams/  
├── core\_app/                 \# Main application (Auth, Dashboard)  
├── masterdata/               \# Aviation & Infrastructure data  
├── schedules/                \# Seasonal planning & Gantt views  
├── flight\_ops/               \# Daily operations & Rolling Window engine  
├── templates/                \# HTML templates  
│   ├── schedules/           \# Gantt & Schedule forms  
│   └── flight\_ops/          \# Daily flight lists  
├── static/                   \# Static assets (CSS, JS, Images)  
├── devops/                   \# DevOps scripts  
├── docs/                     \# Detailed documentation  
└── releases/                 \# Release notes

## **🛠️ Installation & Setup**

### **Prerequisites**

* Python 3.12+  
* Docker & Docker Compose  
* Git  
* WSL2 (if on Windows)

### **Quick Start**

1. **Clone the repository**  
   git clone \[<https://github.com/Iotonix/osams.git\>](<https://github.com/Iotonix/osams.git>)  
   cd osams

2. **Set up environment variables**  
   cp .env.example .env  
   \# Edit .env with your configuration

3. **Start the database**  
   docker-compose up \-d timescaledb

4. **Install Python dependencies**  
   pip install \-r requirements.txt

5. **Run database migrations**  
   python manage.py migrate

6. **Create a superuser**  
   ./create\_superuser.sh  
   \# Or manually:  
   \# python manage.py createsuperuser

7. **Start the development server**  
   python manage.py runserver

8. **Access the application**  
   * Login: [http://localhost:8000/login/](https://www.google.com/search?q=http://localhost:8000/login/)  
   * Dashboard: [http://localhost:8000/](https://www.google.com/search?q=http://localhost:8000/)  
   * Admin: [http://localhost:8000/admin/](https://www.google.com/search?q=http://localhost:8000/admin/)

### **Default Credentials**

After running create\_superuser.sh:

* **Username:** admin  
* **Password:** admin123  
* **Email:** [ralf.hundertmark@yahoo.com](mailto:ralf.hundertmark@yahoo.com)

## **🐳 Docker Deployment**

### **Build the image**

./build\_manually.sh

### **Run with Docker Compose**

docker-compose up \-d

## **📦 Core Modules**

### **✅ Master Data (Implemented)**

Comprehensive management of airport reference data:

* **Aviation:** Airlines, Airports, Aircraft Types, Routes  
* **Infrastructure:** Terminals, Gates, Stands, Check-in Counters, Baggage Carousels, Runways, Ground Handlers

### **✅ Schedules & Visualization (Implemented)**

* **Seasonal Flights:** Template-based flight schedules  
* **Interactive Gantt Chart:** **\[NEW\]** Visual timeline of gate/stand/carousel usage powered by Vis.js  
* **Seeding Command:** Generate realistic seasonal traffic

### **✅ Flight Operations (Implemented)**

* **Daily Flights:** Concrete flight instances with status tracking  
* **Rolling Window Strategy:** Auto-generation of 90-day windows  
* **Operations Dashboard:** Live view of daily movements with status filtering

### **🚧 Operational Modules (Planned)**

1. **fids** \- Real-time Flight Information Display System (v0.6)  
2. **billing** \- Aeronautical fee calculation  
3. **bi\_stats** \- Analytics dashboards using TimescaleDB hyper-functions

## **🤝 Contributing**

We welcome contributions\! Please read our [**Contributing Guide**](https://www.google.com/search?q=CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### **Basic Workflow**

1. Fork the repository  
2. Create a feature branch (git checkout \-b feature/amazing-feature)  
3. Commit your changes (git commit \-m 'Add amazing feature')  
4. Push to the branch (git push origin feature/amazing-feature)  
5. Open a Pull Request

## **📝 License**

This project is open source. See LICENSE file for details.

## **👥 Team**

* **Developer:** Ralf Hundertmark  
* **Organization:** Iotonix

## **📮 Contact**

For questions or support, please open an issue on GitHub or contact the development team.

**Built with ❤️ for the aviation industry**
