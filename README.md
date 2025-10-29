## Overview

Squid Proxy Manager is a web-based management interface for Squid proxy servers. It provides an intuitive dashboard for configuring, monitoring, and managing your Squid proxy installation through a modern web interface.

### Features

-   Real-time proxy status monitoring
-   Configuration management via web UI
-   Access log viewing and analysis
-   Service control (reload/restart)
-   Statistics dashboard
-   Advanced features (SSL Bump, Authentication)
-   Access Control List (ACL) management (planned)

----------

<details>
  <summary><h2> Architecture</h2></summary>

### Technology Stack

-   **OS**: Debian 11
-   **Frontend**: HTML5, TailwindCSS, Vanilla JavaScript
-   **Backend**: Python 3 with Flask framework
-   **Web Server**: Nginx (reverse proxy)
-   **Proxy Server**: Squid
-   **Service Management**: systemd

### Component Layout

```
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
```
----------
</details>

<details>
  <summary><h2>Installation & Setup</h2></summary>

### Prerequisites


```bash
# Required packages
- Python 3.6+
- Nginx
- Squid
- systemd
```

### Directory Structure

```
/opt/squid-gui/
├── app.py                  # Flask backend application

/var/www/squid-gui/
├── index.html             # Frontend interface

/etc/nginx/sites-available/
├── squid-gui              # Nginx configuration

/etc/squid/
├── squid.conf             # Squid main config
└── squid.conf.backup      # Automatic backup
```

### Installation Steps

#### 1. Install Python Dependencies


```bash
cd /opt/squid-gui
pip3 install flask flask-cors
```

#### 2. Configure Nginx

Create `/etc/nginx/sites-available/squid-gui`:


```nginx
server {
    listen 8080;
    server_name _;
    root /var/www/squid-gui;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:


```bash
ln -s /etc/nginx/sites-available/squid-gui /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

#### 3. Create Systemd Service

Create `/etc/systemd/system/squid-gui.service`:


```ini
[Unit]
Description=Squid GUI Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/squid-gui
ExecStart=/usr/bin/python3 /opt/squid-gui/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:


```bash
systemctl daemon-reload
systemctl enable squid-gui
systemctl start squid-gui
```

#### 4. Set Permissions


```bash
# Ensure proper permissions
chmod +x /opt/squid-gui/app.py
chown -R www-data:www-data /var/www/squid-gui

# Backend needs root access to modify squid config
# Already configured to run as root in systemd service
```

#### 5. Verify Installation


```bash
# Check backend status
systemctl status squid-gui

# Check if backend is responding
curl http://localhost:5001/api/health

# Access web interface
# Open browser to: http://your-server:8080
```

----------

## Configuration

### Backend Configuration (app.py)

#### Key Variables


```python
SQUID_CONF = '/etc/squid/squid.conf'           # Main config file
SQUID_CONF_BACKUP = '/etc/squid/squid.conf.backup'  # Backup file
```

#### Changing Backend Port

Edit `/opt/squid-gui/app.py`:


```python
app.run(host='0.0.0.0', port=5001, debug=False)
```

Change `5001` to your desired port, then restart service.

#### Changing Frontend Port

Edit `/etc/nginx/sites-available/squid-gui`:


```nginx
listen 8080;  # Change to desired port
```

Then reload nginx: `systemctl reload nginx`

### Squid Configuration Requirements

The application manages these Squid configuration directives:

-   `http_port` - Proxy listening port
-   `cache_mem` - Memory allocated for cache
-   `visible_hostname` - Hostname visible to clients
-   `cache_dir` - Cache directory location
-   `dns_nameservers` - DNS servers to use
-   `access_log` - Access log file path
-   `cache_log` - Cache log file path
-   `maximum_object_size` - Maximum cached object size

----------
</details>

<details>
  <summary><h2>API Reference</h2></summary>

### Base URL

```
http://localhost:5001/api
```

### Endpoints

#### Health Check


```http
GET /api/health
```

**Response:**


```json
{
  "status": "ok",
  "message": "Squid GUI Backend is running"
}
```

#### Get Configuration


```http
GET /api/config
```

**Response:**

```json
{
  "http_port": "3128",
  "cache_dir": "/var/spool/squid",
  "cache_mem": "256 MB",
  "visible_hostname": "squid-proxy",
  "dns_nameservers": "8.8.8.8 8.8.4.4",
  "access_log": "/var/log/squid/access.log",
  "cache_log": "/var/log/squid/cache.log",
  "maximum_object_size": "4096 KB"
}
```

#### Update Configuration


```http
POST /api/config
Content-Type: application/json
```

**Request Body:**


```json
{
  "http_port": "3128",
  "cache_mem": "512 MB",
  "visible_hostname": "my-proxy"
}
```

**Response:**


```json
{
  "success": true,
  "message": "Configuration updated"
}
```

#### Get Proxy Status


```http
GET /api/status
```

**Response:**


```json
{
  "running": true,
  "status": "active"
}
```

#### Reload Squid


```http
POST /api/reload
```

**Response:**


```json
{
  "success": true,
  "output": "",
  "error": ""
}
```

#### Restart Squid


```http
POST /api/restart
```

**Response:**


```json
{
  "success": true,
  "output": "",
  "error": ""
}
```

#### Get Access Logs


```http
GET /api/logs?lines=100
```

**Query Parameters:**

-   `lines` (optional): Number of log lines to retrieve (default: 100)

**Response:**


```json
[
  {
    "timestamp": "2025-10-29 14:00:00",
    "client": "192.168.1.1",
    "method": "GET",
    "url": "example.com",
    "status": "200",
    "size": "1024"
  }
]
```

#### Get Statistics


```http
GET /api/stats
```

**Response:**

```json
{
  "uptime": "5d 12h 34m",
  "requests": "125,847",
  "cacheHitRate": "67.8%",
  "bandwidth": "4.2 GB",
  "activeConnections": "23"
}
```
</details>

----------

## Known Limitations

1.  **ACL Management**: Not yet implemented - requires manual editing of `squid.conf`
2.  **SSL Bump**: Interface provides toggles but requires manual certificate setup
3.  **Authentication**: Enable checkbox doesn't configure actual auth - manual setup required
4.  **Statistics**: Currently returns placeholder data - needs squidclient integration
5.  **Log Parsing**: Simplified parsing - may not match actual Squid log format
6.  **Multi-User**: No built-in user management or role-based access control
7.  **Validation**: Limited input validation on configuration values

----------

## Roadmap / Future Enhancements

-   Full ACL management interface
-   Real-time statistics from squidclient
-   Proper Squid log parsing
-   Configuration validation before saving
-   Backup/restore functionality
-   Multi-user support with authentication
-   SSL certificate generation wizard
-   Bandwidth monitoring graphs
-   Cache performance analytics
-   Email alerts for issues
-   Configuration templates
-   Dark mode theme

----------

## Support & Resources

### Official Squid Documentation

-   Squid Website: [http://www.squid-cache.org/](http://www.squid-cache.org/)
-   Squid Configuration: [http://www.squid-cache.org/Doc/config/](http://www.squid-cache.org/Doc/config/)

### Application Files

-   Backend: `/opt/squid-gui/app.py`
-   Frontend: `/var/www/squid-gui/index.html`
-   Nginx Config: `/etc/nginx/sites-available/squid-gui`
-   Service File: `/etc/systemd/system/squid-gui.service`

### Logs Locations

-   Backend Logs: `journalctl -u squid-gui`
-   Nginx Logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
-   Squid Logs: `/var/log/squid/access.log`, `/var/log/squid/cache.log`

----------

## License

This application is provided as-is for managing Squid proxy servers. Ensure compliance with your organization's policies when deploying.

----------

## Changelog

### Version 1.0 (Current)

-   Initial release
-   Basic configuration management
-   Service control (reload/restart)
-   Log viewing
-   Status monitoring
-   Advanced settings UI (SSL Bump, Auth)
