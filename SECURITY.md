# Security Hardening Guide

This document provides comprehensive security guidance for deploying Glassmorphic File Manager in production environments.

## Table of Contents

1. [Authentication Security](#authentication-security)
2. [Network Security](#network-security)
3. [System Hardening](#system-hardening)
4. [File Upload Security](#file-upload-security)
5. [Monitoring & Logging](#monitoring--logging)
6. [Backup & Recovery](#backup--recovery)
7. [Security Checklist](#security-checklist)

---

## Authentication Security

### Strong Passwords

Generate a cryptographically secure password:
```bash
# Generate a 24-character random password
openssl rand -base64 18
```

Use the password hash generator:
```bash
/opt/glassfile/venv/bin/python3 -c "
from werkzeug.security import generate_password_hash
import getpass
password = getpass.getpass('Enter password: ')
print(generate_password_hash(password, method='scrypt'))
"
```

### API Key Management

**Best Practices:**
- Generate unique API keys for each client/user
- Rotate API keys periodically (every 90 days recommended)
- Store API keys securely (never in version control)
- Use environment variables for automated deployments

Generate a secure API key:
```bash
openssl rand -base64 32 | tr -d '/+=' | head -c 43
```

**Multiple API Keys:**
```yaml
security:
  api_keys:
    - 'key-for-cli-user-1'
    - 'key-for-automated-backup'
    - 'key-for-monitoring-system'
```

### Session Security

Configure secure session settings in `config.yaml`:
```yaml
security:
  session_lifetime: 1800  # 30 minutes (reduce for sensitive environments)
```

The application automatically:
- Uses secure, HTTP-only session cookies
- Regenerates session IDs on login
- Clears sessions completely on logout

### IP Whitelisting

Restrict management access to specific IP addresses:
```yaml
security:
  ip_whitelist:
    - '192.168.1.0/24'    # Local network
    - '10.0.0.5'          # Specific admin machine
    - '203.0.113.10'      # Office IP
```

---

## Network Security

### HTTPS Configuration

**Always use HTTPS in production.** HTTP transmits credentials in plaintext.

1. Install certbot:
   ```bash
   sudo apt update
   sudo apt install certbot python3-certbot-nginx
   ```

2. Obtain certificate:
   ```bash
   sudo certbot --nginx -d files.yourdomain.com
   ```

3. Verify auto-renewal:
   ```bash
   sudo certbot renew --dry-run
   ```

### Nginx Security Headers

The provided `nginx.conf.example` includes essential security headers. Verify they're active:

```nginx
# Essential security headers
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# HSTS (enable after confirming HTTPS works)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Rate Limiting

The Nginx configuration includes rate limiting to prevent abuse:

```nginx
# In http block
limit_req_zone $binary_remote_addr zone=filemanager:10m rate=10r/s;

# In location blocks
limit_req zone=filemanager burst=20 nodelay;
```

Adjust based on your expected traffic:
- `rate=10r/s` - 10 requests per second per IP
- `burst=20` - Allow bursts up to 20 requests
- `nodelay` - Process burst requests immediately

### Firewall Configuration

```bash
# Reset UFW rules (careful - may disconnect SSH)
sudo ufw reset

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (adjust port if needed)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Verify rules
sudo ufw status verbose
```

### Fail2ban Configuration

Protect against brute-force attacks:

1. Install fail2ban:
   ```bash
   sudo apt install fail2ban
   ```

2. Create `/etc/fail2ban/jail.d/glassfile.conf`:
   ```ini
   [glassfile]
   enabled = true
   port = http,https
   filter = glassfile
   logpath = /var/log/glassfile/error.log
   maxretry = 5
   findtime = 300
   bantime = 3600
   ```

3. Create `/etc/fail2ban/filter.d/glassfile.conf`:
   ```ini
   [Definition]
   failregex = ^.*Authentication failed from <HOST>.*$
               ^.*Invalid API key from <HOST>.*$
   ignoreregex =
   ```

4. Restart fail2ban:
   ```bash
   sudo systemctl restart fail2ban
   ```

---

## System Hardening

### Service Account Security

The installation creates a dedicated service user with minimal privileges:

```bash
# Verify user has no login shell
grep filemanager /etc/passwd
# Should show: filemanager:x:...:...::/nonexistent:/bin/false
```

### Systemd Security Features

The service file includes these hardening options:

```ini
[Service]
# Prevent privilege escalation
NoNewPrivileges=true

# Private /tmp directory
PrivateTmp=true

# Read-only system directories
ProtectSystem=strict

# Cannot access /home directories
ProtectHome=true

# Only allow writes to specific paths
ReadWritePaths=/opt/glassfile/static/files /opt/glassfile/fileserver.log

# Resource limits
LimitNOFILE=65536
MemoryMax=512M
CPUQuota=100%
```

Additional hardening (add to service file):

```ini
[Service]
# Additional security options
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectKernelLogs=true
ProtectControlGroups=true
ProtectClock=true
RestrictRealtime=true
RestrictSUIDSGID=true
PrivateDevices=true
CapabilityBoundingSet=
AmbientCapabilities=
SystemCallFilter=@system-service
SystemCallArchitectures=native
```

### File Permissions

Verify correct permissions:

```bash
# Check ownership
ls -la /opt/glassfile/

# Expected output:
# drwxr-xr-x filemanager filemanager  config.yaml (should be 600)
# drwxr-xr-x filemanager filemanager  static/
# -rw-r--r-- filemanager filemanager  fileserver.py
# -rwxr-xr-x filemanager filemanager  filemanager

# Fix if needed
sudo chown -R filemanager:filemanager /opt/glassfile
sudo chmod 600 /opt/glassfile/config.yaml
sudo chmod 755 /opt/glassfile/static/files
```

### Separate Storage Volume

For better security and quota management, use a separate volume for file storage:

```bash
# Create dedicated partition/volume
sudo mkfs.ext4 /dev/sdb1

# Mount with noexec,nosuid options
echo '/dev/sdb1 /opt/glassfile/static/files ext4 defaults,noexec,nosuid,nodev 0 2' | sudo tee -a /etc/fstab

sudo mount -a
sudo chown filemanager:filemanager /opt/glassfile/static/files
```

---

## File Upload Security

### File Size Limits

Configure maximum file size in `config.yaml`:

```yaml
storage:
  max_file_size: 104857600  # 100MB
```

Also configure in Nginx:

```nginx
client_max_body_size 100M;
```

### Extension Filtering

Restrict allowed file types:

```yaml
storage:
  allowed_extensions:
    - '.pdf'
    - '.doc'
    - '.docx'
    - '.xls'
    - '.xlsx'
    - '.txt'
    - '.jpg'
    - '.jpeg'
    - '.png'
    - '.gif'
    - '.zip'
```

### Dangerous Extensions to Block

If allowing all extensions, consider blocking these:

```yaml
storage:
  # Block executable and script files
  blocked_extensions:
    - '.exe'
    - '.bat'
    - '.cmd'
    - '.sh'
    - '.ps1'
    - '.php'
    - '.jsp'
    - '.asp'
    - '.aspx'
    - '.cgi'
    - '.pl'
```

### Antivirus Scanning

Integrate ClamAV for upload scanning:

1. Install ClamAV:
   ```bash
   sudo apt install clamav clamav-daemon
   sudo systemctl enable clamav-daemon
   sudo freshclam
   ```

2. Scan files in the upload handler (requires code modification):
   ```python
   import subprocess

   def scan_file(filepath):
       result = subprocess.run(
           ['clamdscan', '--no-summary', filepath],
           capture_output=True, text=True
       )
       return result.returncode == 0  # 0 = clean, 1 = infected
   ```

---

## Monitoring & Logging

### Log Rotation

Create `/etc/logrotate.d/glassfile`:

```
/var/log/glassfile/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 filemanager filemanager
    sharedscripts
    postrotate
        systemctl reload glassfile 2>/dev/null || true
    endscript
}
```

### Log Monitoring

Monitor for security events:

```bash
# Watch for authentication failures
tail -f /var/log/glassfile/error.log | grep -i "auth\|login\|failed"

# Monitor access patterns
tail -f /var/log/glassfile/access.log | grep -E "POST|DELETE|PUT"
```

### Alerting

Set up alerts for suspicious activity:

```bash
# Simple script for email alerts
#!/bin/bash
LOG="/var/log/glassfile/error.log"
THRESHOLD=10
EMAIL="admin@example.com"

COUNT=$(grep -c "Authentication failed" "$LOG" 2>/dev/null || echo 0)
if [ "$COUNT" -gt "$THRESHOLD" ]; then
    echo "Warning: $COUNT failed auth attempts" | mail -s "Glassfile Security Alert" "$EMAIL"
fi
```

### Health Monitoring

Use the health endpoint for monitoring:

```bash
# Simple health check script
curl -s http://localhost:8080/health | jq -e '.status == "healthy"' || echo "ALERT: Service unhealthy"
```

---

## Backup & Recovery

### Backup Strategy

1. **Configuration backup:**
   ```bash
   sudo cp /opt/glassfile/config.yaml /backup/glassfile/config.yaml.$(date +%Y%m%d)
   ```

2. **File storage backup:**
   ```bash
   sudo rsync -av --delete /opt/glassfile/static/files/ /backup/glassfile/files/
   ```

3. **Full backup script:**
   ```bash
   #!/bin/bash
   BACKUP_DIR="/backup/glassfile/$(date +%Y%m%d)"
   mkdir -p "$BACKUP_DIR"

   # Stop service briefly for consistent backup
   sudo systemctl stop glassfile

   # Backup files
   sudo cp -a /opt/glassfile/config.yaml "$BACKUP_DIR/"
   sudo tar -czf "$BACKUP_DIR/files.tar.gz" -C /opt/glassfile/static files/

   # Restart service
   sudo systemctl start glassfile

   # Remove old backups (keep 30 days)
   find /backup/glassfile -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
   ```

### Recovery Procedure

1. Stop the service:
   ```bash
   sudo systemctl stop glassfile
   ```

2. Restore files:
   ```bash
   sudo cp /backup/glassfile/YYYYMMDD/config.yaml /opt/glassfile/
   sudo tar -xzf /backup/glassfile/YYYYMMDD/files.tar.gz -C /opt/glassfile/static/
   ```

3. Fix permissions:
   ```bash
   sudo chown -R filemanager:filemanager /opt/glassfile
   sudo chmod 600 /opt/glassfile/config.yaml
   ```

4. Start the service:
   ```bash
   sudo systemctl start glassfile
   ```

---

## Security Checklist

### Initial Deployment

- [ ] Changed default admin password
- [ ] Generated unique API keys
- [ ] Configured HTTPS with valid certificate
- [ ] Enabled firewall (UFW)
- [ ] Set up fail2ban
- [ ] Configured log rotation
- [ ] Set appropriate file size limits
- [ ] Reviewed allowed file extensions
- [ ] Verified file permissions
- [ ] Tested backup and recovery procedures

### Ongoing Maintenance

- [ ] Rotate API keys every 90 days
- [ ] Review access logs weekly
- [ ] Update system packages monthly
- [ ] Renew SSL certificates (automated with certbot)
- [ ] Test backups monthly
- [ ] Review security headers quarterly
- [ ] Audit user access annually

### Incident Response

- [ ] Document security contacts
- [ ] Define incident severity levels
- [ ] Create response procedures
- [ ] Test recovery procedures
- [ ] Maintain audit trail

---

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** disclose it publicly
2. Email security details to the maintainer
3. Allow reasonable time for a fix
4. Coordinate disclosure timeline

---

## Additional Resources

- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Nginx Security Best Practices](https://nginx.org/en/docs/http/configuring_https_servers.html)
