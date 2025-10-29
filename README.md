Overview
Squid Proxy Manager is a web-based management interface for Squid proxy servers. It provides an intuitive dashboard for configuring, monitoring, and managing your Squid proxy installation through a modern web interface.
Features

Real-time proxy status monitoring
Configuration management via web UI
Access log viewing and analysis
Service control (reload/restart)
Statistics dashboard
Advanced features (SSL Bump, Authentication)
Access Control List (ACL) management (planned)


Architecture
Technology Stack

Frontend: HTML5, TailwindCSS, Vanilla JavaScript
Backend: Python 3 with Flask framework
Web Server: Nginx (reverse proxy)
Proxy Server: Squid
Service Management: systemd

Component Layout
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP :8080
┌──────▼──────┐
│    Nginx    │ (Reverse Proxy)
└──────┬──────┘
       │
       ├─ Static files (/var/www/squid-gui/)
       │
       └─ API requests (/api/*) → http://localhost:5001
                                   │
                            ┌──────▼───────┐
                            │ Flask Backend│ (/opt/squid-gui/)
                            └──────┬───────┘
                                   │
                            ┌──────▼───────────────┐
                            │ Squid Config & Logs  │
                            │ /etc/squid/          │
                            │ /var/log/squid/      │
                            └──────────────────────┘

Installation & Setup
Prerequisites
bash# Required packages
- Python 3.6+
- Nginx
- Squid
- systemd
Directory Structure
/opt/squid-gui/
├── app.py                  # Flask backend application

/var/www/squid-gui/
├── index.html             # Frontend interface

/etc/nginx/sites-available/
├── squid-gui              # Nginx configuration

/etc/squid/
├── squid.conf             # Squid main config
└── squid.conf.backup      # Automatic backup
