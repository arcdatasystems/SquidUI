## User Guide

### Accessing the Interface

1.  Open web browser
2.  Navigate to `http://your-server-ip:8080`
3.  The dashboard will load automatically

### Dashboard Overview

#### Header Section

-   **Status Indicator**: Shows if Squid is running (green) or stopped (red)
-   **Application Title**: "Squid Proxy Manager"

### Navigation Tabs

1.  **Configuration** - Basic proxy settings
2.  **Advanced** - SSL Bump and authentication
3.  **Access Control** - ACL management (planned)
4.  **Monitoring** - Statistics and quick actions
5.  **Logs** - View access logs

## Configuration Tab

#### Modifying Basic Settings

1.  Navigate to **Configuration** tab
2.  Edit any field (e.g., HTTP Port, Cache Memory, Hostname)
3.  Click **"Save Configuration"** button
4.  Click **"Reload Squid"** to apply changes

**Note**: Configuration changes are saved to `/etc/squid/squid.conf` and a backup is automatically created.

#### Available Settings

-   **HTTP Port**: Port where Squid listens for connections
-   **Cache Dir**: Directory for storing cached content
-   **Cache Mem**: RAM allocated for caching
-   **Visible Hostname**: Hostname shown to clients
-   **DNS Nameservers**: DNS servers used by proxy
-   **Access Log**: Path to access log file
-   **Cache Log**: Path to cache log file
-   **Maximum Object Size**: Largest object to cache

## Advanced Tab

#### SSL Bump (HTTPS Interception)

1.  Check **"Enable SSL Bump"** checkbox
2.  Configure SSL Bump Port (default: 3129)
3.  Set Certificate Path (default: `/etc/squid/ssl_cert/myCA.pem`)
4.  Click **"Save Advanced Configuration"**

**Warning**: SSL Bump requires additional certificate setup and configuration not covered by this interface.

#### Proxy Authentication

1.  Check **"Enable Authentication"** checkbox
2.  Click **"Save Advanced Configuration"**

**Note**: Advanced features require manual Squid configuration.

## Monitoring Tab

#### Statistics Display

View real-time proxy statistics:

-   Proxy uptime
-   Total requests processed
-   Cache hit rate percentage
-   Total bandwidth used
-   Active connections

#### Quick Actions

-   **Reload Squid**: Apply configuration changes without downtime
-   **Clear Cache**: Remove all cached content
-   **Rotate Logs**: Archive current logs and start fresh

## Logs Tab

#### Viewing Access Logs

1.  Navigate to **Logs** tab
2.  View recent proxy access entries
3.  Click **Refresh** button to update

#### Log Information Displayed

-   **Timestamp**: When request occurred
-   **Client IP**: Source IP address
-   **Method**: HTTP method (GET, POST, etc.)
-   **URL**: Requested URL
-   **Status**: HTTP status code
-   **Size**: Response size in bytes

----------

# Troubleshooting

### Backend Not Starting

**Symptom**: Cannot access web interface or API

**Solutions**:


```bash
# Check service status
systemctl status squid-gui

# View logs
journalctl -u squid-gui -f

# Check if port is in use
netstat -tlnp | grep 5001

# Verify Python dependencies
pip3 list | grep -E 'flask|flask-cors'
```

### Permission Errors

**Symptom**: "Permission denied" errors in logs

**Solutions**:


```bash
# Ensure backend runs as root (required for squid config modification)
# Check systemd service file has User=root

# Verify squid config permissions
ls -l /etc/squid/squid.conf

# Ensure squid log directory is accessible
ls -ld /var/log/squid/
```

### Nginx 502 Bad Gateway

**Symptom**: Web interface loads but shows 502 error

**Solutions**:


```bash
# Check if backend is running
systemctl status squid-gui
curl http://localhost:5001/api/health

# Check nginx error logs
tail -f /var/log/nginx/error.log

# Verify nginx proxy configuration
nginx -t
```

### Configuration Not Saving

**Symptom**: Changes don't persist after saving

**Solutions**:


```bash
# Verify squid config file exists
ls -l /etc/squid/squid.conf

# Check backend has write permissions
# Backend must run as root or have write access

# Check for SELinux issues (if applicable)
sestatus
ausearch -m AVC -ts recent
```

### Squid Won't Reload

**Symptom**: Reload button fails or Squid doesn't restart

**Solutions**:

```bash
# Test squid configuration
squid -k parse

# Check squid status
systemctl status squid

# Try manual reload
systemctl reload squid

# Check squid logs
tail -f /var/log/squid/cache.log
```

### Logs Not Displaying

**Symptom**: Logs tab shows "No logs available"

**Solutions**:


```bash
# Verify log file exists
ls -l /var/log/squid/access.log

# Check log file permissions
# Backend needs read access

# Verify squid is logging
tail -f /var/log/squid/access.log

# Check if log path in squid.conf matches
grep access_log /etc/squid/squid.conf
```

----------

# Security Considerations

### Access Control

-   The web interface runs on port 8080 (default) - consider firewall rules
-   Backend API runs on localhost:5001 (not exposed externally)
-   Only nginx has external access

### Recommended Security Measures

#### 1. Add Authentication to Nginx


```nginx
server {
    listen 8080;
    auth_basic "Squid Admin";
    auth_basic_user_file /etc/nginx/.htpasswd;
    # ... rest of config
}
```

Create password file:


```bash
htpasswd -c /etc/nginx/.htpasswd admin
```

#### 2. Enable HTTPS


```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... rest of config
}
```

#### 3. Restrict IP Access


```nginx
server {
    listen 8080;
    allow 192.168.1.0/24;
    deny all;
    # ... rest of config
}
```

#### 4. Run Backend as Non-Root (Advanced)

Requires setting up sudo rules for specific squid commands:


```bash
# Add to /etc/sudoers.d/squid-gui
squidgui ALL=(ALL) NOPASSWD: /bin/systemctl reload squid
squidgui ALL=(ALL) NOPASSWD: /bin/systemctl restart squid
```

### File Permissions


```bash
# Backend application
chmod 750 /opt/squid-gui/app.py
chown root:root /opt/squid-gui/app.py

# Frontend files
chmod 755 /var/www/squid-gui
chmod 644 /var/www/squid-gui/index.html
chown -R www-data:www-data /var/www/squid-gui

# Squid configuration
chmod 640 /etc/squid/squid.conf
chown root:proxy /etc/squid/squid.conf
```

----------

# Maintenance

### Backup Configuration


```bash
# Manual backup
cp /etc/squid/squid.conf /etc/squid/squid.conf.backup.$(date +%Y%m%d)

# Automated backups (add to cron)
0 2 * * * cp /etc/squid/squid.conf /backup/squid.conf.$(date +\%Y\%m\%d)
```

### Log Rotation

Squid logs are typically managed by logrotate. Verify configuration:


```bash
cat /etc/logrotate.d/squid
```

### Updating the Application

#### Backend Updates


```bash
systemctl stop squid-gui
# Replace app.py with new version
systemctl start squid-gui
systemctl status squid-gui
```

#### Frontend Updates

bash

```bash
# Replace index.html
cp new-index.html /var/www/squid-gui/index.html
# No service restart needed - refresh browser
```

### Monitoring Service Health

bash

```bash
# Check all services
systemctl status squid
systemctl status squid-gui
systemctl status nginx

# Monitor logs in real-time
journalctl -u squid-gui -f
tail -f /var/log/nginx/access.log
tail -f /var/log/squid/access.log
```
