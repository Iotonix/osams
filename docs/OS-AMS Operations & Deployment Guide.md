# **🛠️ OS-AMS Operations & Deployment Guide**

## **1\. Architecture Overview**

* **App Server:** Python 3.12 / Django 5.2 (Gunicorn in Prod)  
* **Database:** PostgreSQL 16 \+ **TimescaleDB** extension (Required)  
* **Package Manager:** uv (Astral) for high-speed builds

## **2\. Development Environment**

### **Prerequisites**

* Docker & Docker Compose  
* (Optional) uv installed locally for fast dependency resolution

### **Quick Start**

\# 1\. Start the database stack (TimescaleDB)  
docker-compose up \-d timescaledb

\# 2\. Build the app image  
./build\_manually.sh

\# 3\. Run the application  
docker-compose up \-d

### **Management Commands**

OS-AMS relies heavily on custom management commands for logic.

**Seeding Data (Dev Only):**

\# Infrastructure  
docker-compose exec osams python manage.py seed\_airport\_infrastructure  
\# Aviation Data (Airlines/Aircraft)  
docker-compose exec osams python manage.py seed\_aviation  
\# Seasonal Schedules  
docker-compose exec osams python manage.py seed\_seasonal\_flights

Operational Cron Jobs:  
In production, these must run daily (via crontab or Celery beat):

1. Generate Rolling Window (00:30):  
   python manage.py generate\_daily\_flights \--days 90 \--incremental  
   Ensures the next 90 days of operations exist in the DB.  
2. Allocate Resources (01:00):  
   python manage.py allocate\_seasonal\_resources  
   Assigns gates/stands to newly generated flights based on logic.

## **3\. Production Deployment**

### **Docker Build Strategy**

We use a multi-stage Dockerfile utilizing uv for faster builds.

* **Base:** python:3.12-slim  
* **Builder:** ghcr.io/astral-sh/uv:0.2.12

### **Environment Variables (.env)**

Ensure these are set in your production environment (e.g., Vultr, AWS).

| Variable | Description | Default/Example |
| :---- | :---- | :---- |
| POSTGRES\_DB | Database Name | osams |
| POSTGRES\_USER | DB User | pgadmin |
| POSTGRES\_HOST | DB Hostname | timescaledb |
| DEBUG | Django Debug Mode | False (CRITICAL for Prod) |
| SECRET\_KEY | Django Secret | **Generate a strong random string** |
| ALLOWED\_HOSTS | Domain Whitelist | airport-sys.com,1.2.3.4 |

### **Deployment Scripts**

* release2vultr.sh: Uses rsync to push code to the production server at /srv/aims/SRC/osams/. Ensure SSH keys are configured.

## **4\. Troubleshooting**

**Issue: "Relation does not exist"**

* **Cause:** Migrations haven't run or TimescaleDB extension isn't enabled.  
* **Fix:** python manage.py migrate

**Issue: "Aircraft wingspan exceeds gate capacity" during Seed**

* **Cause:** seed\_airport\_infrastructure created small gates, but seed\_seasonal\_flights is trying to schedule an A380.  
* **Fix:** The seeder logs warnings. In production, manually assign a larger gate in the Admin panel.