# Security Configuration & Server Hardening

This document outlines the required security steps for deploying the Open Source Airport Management System (OSAMS) on a production Ubuntu 24.04 server.

## 1. Network Firewall (UFW) Configuration

We strictly control inbound traffic. By default, all incoming connections should be denied, and only specific services allowed.

### Required Ports

Run the following commands on your server to configure the `ufw` (Uncomplicated Firewall).

```bash
# 1. Reset UFW to default (Deny Incoming, Allow Outgoing)
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 2. Web Traffic (Required for OSAMS Interface)
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# 3. Secure Management (Custom SSH Port)
# We move SSH from port 22 to 50022 to reduce automated bot attacks.
sudo ufw allow 50022/tcp

# 4. Database Access (Optional/Remote Admin)
# Only open this if you need to connect to PostgreSQL remotely.
# WARNING: It is highly recommended to restrict this to your specific IP address.
sudo ufw allow 55432/tcp

# 5. Enable the Firewall
sudo ufw enable
