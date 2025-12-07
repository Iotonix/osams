# **✈️ OS-AMS: Open Source Airport Management System**

## **1\. Project Overview**

**OS-AMS** is a modular, high-performance Airport Management System designed to replace expensive legacy infrastructure for Small-to-Medium Airports (SMAs). Built on **Django 5**, it leverages **TimescaleDB** for handling high-frequency operational time-series data and utilizes a custom **Bootstrap 5** frontend for a responsive, modern user interface.

The system automates critical airport domains including Flight Scheduling, Resource Allocation (Gates/Check-in), Flight Information Displays (FIDS), and Aeronautical Billing.

## **2\. Technology Stack**

### **Backend & Application Layer**

* **Framework:** Python Django 5.0  
* **Architecture:** Modular Monolith (separated into functional apps).  
* **Asynchronous Tasks:** Celery (for heavy calculation tasks like allocation logic and schedule processing).  
* **Real-time:** Django Channels (ASGI) for FIDS updates.

### **Database & Storage**

* **Core Database:** **TimescaleDB** (PostgreSQL 16 based).  
  * *Reasoning:* Optimized for time-series flight tracking and resource utilization logs.  
* **Cache & Message Broker:** **Redis** (used for Celery task queue and Django Channels layer).

### **Frontend & UI**

* **Framework:** **Bootstrap 5** (Custom Template).  
* **Design System:** Supports **Light** and **Dark** modes (see artefacts/ folder).  
* **Visualization:** Chart.js or ApexCharts for BI Dashboards.

## **3\. Development Environment Setup**

### **Database Configuration**

We use a containerized TimescaleDB instance. Ensure your docker-compose.yml includes the following service definition:

services:  
  timescaledb:  
    image: timescale/timescaledb:latest-pg16  
    container\_name: timescaledb  
    ports:  
      \- "5432:5432"  
    restart: always  
    networks:  
      \- aitNet  
    environment:  
      \- POSTGRES\_DB=hugo  
      \- POSTGRES\_USER=ait  
      \- POSTGRES\_PASSWORD="aiait1234"  
    volumes:  
      \- TimescaleDBVolume:/var/lib/postgresql/data

### **Artefacts**

UI References and Assets are located in .\\artefacts:

* **Logo:** logo.jpg  
* **UI Themes:** light.jpg (Day Mode), dark.jpg (Night/Operation Center Mode).

## **4\. Core Modules**

1. **masterdata**: Manages physical assets (Gates, Terminals) and Airline profiles.  
2. **schedules**: Handles Seasonal and Daily flight plans (SSIM import).  
3. **allocation**: Constraint-based engine for assigning Gates and Check-in counters.  
4. **fids**: Real-time Flight Information Display System (WebSocket driven).  
5. **billing**: Calculates aeronautical fees (landing, parking, passenger).  
6. **bi\_stats**: Analytics dashboards using TimescaleDB hyper-functions.

## **5\. Getting Started**

1. Clone the repository.  
2. Start the database: docker-compose up \-d timescaledb  
3. Install requirements: pip install \-r requirements.txt  
4. Run migrations: python manage.py migrate  
5. Start the development server: python manage.py runserver  
6. Start Celery worker: celery \-A os\_ams worker \-l info
