# Glassmorphic File Manager

A stunning, secure file hosting solution featuring an Apple-inspired glassmorphism web interface and CLI management tools. Designed for self-hosted file sharing with direct download links accessible via wget.

## Features

- **Beautiful Glassmorphic UI** - Premium dark mode aesthetic with animated gradient blobs, mouse parallax effects, and smooth animations
- **Secure Authentication** - Password-protected web interface and API key authentication for CLI
- **Direct Download Links** - Public file URLs compatible with wget, curl, and browsers
- **CLI Management Tool** - Full-featured command-line interface with progress bars and colored output
- **Responsive Design** - Works seamlessly on mobile, tablet, and desktop
- **Accessibility** - Keyboard navigation, screen reader support, reduced motion preferences
- **Production Ready** - Systemd service, Nginx configuration, and installation script included

## Quick Start

### Prerequisites

- Debian/Ubuntu Linux server
- Python 3.8 or higher
- Root/sudo access (for installation)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/glassfile.git
   cd glassfile
   ```

2. Run the installation script:
   ```bash
   sudo ./install.sh
   ```

3. Save the credentials displayed during installation:
   - Admin password (for web login)
   - API key (for CLI tool)

4. Access the web interface:
   ```
   http://your-server:8080
   ```

### Manual Installation

If you prefer manual installation:

```bash
# Create service user
sudo useradd --system --no-create-home --shell /bin/false filemanager

# Create directories
sudo mkdir -p /opt/glassfile/static/files
sudo mkdir -p /var/log/glassfile

# Copy files
sudo cp fileserver.py filemanager requirements.txt /opt/glassfile/
sudo cp -r templates /opt/glassfile/

# Set up Python virtual environment
sudo python3 -m venv /opt/glassfile/venv
sudo /opt/glassfile/venv/bin/pip install -r /opt/glassfile/requirements.txt

# Generate credentials and create config.yaml (see Configuration section)

# Set permissions
sudo chown -R filemanager:filemanager /opt/glassfile /var/log/glassfile
sudo chmod 755 /opt/glassfile/filemanager
sudo chmod 600 /opt/glassfile/config.yaml

# Install and start service
sudo cp fileserver.service /etc/systemd/system/glassfile.service
sudo systemctl daemon-reload
sudo systemctl enable --now glassfile
```

## Configuration

The configuration file is located at `/opt/glassfile/config.yaml`:

```yaml
server:
  host: '0.0.0.0'          # Listen address
  port: 8080               # Listen port
  debug: false             # Debug mode (disable in production)

storage:
  directory: './static/files'    # File storage directory
  max_file_size: 104857600       # Max upload size (100MB)
  allowed_extensions: null        # null = all, or ['.pdf', '.jpg', ...]

security:
  admin_password_hash: '...'     # Generated password hash
  api_keys:
    - 'your-api-key-here'        # API keys for CLI access
  session_lifetime: 3600         # Session timeout (seconds)
  ip_whitelist: []               # Empty = all allowed

display:
  files_per_page: 50             # Files per page
  date_format: 'relative'        # 'relative' or 'absolute'
```

### Generating Credentials

Generate a password hash:
```bash
/opt/glassfile/venv/bin/python3 -c "
from werkzeug.security import generate_password_hash
print(generate_password_hash('your-password'))
"
```

Generate an API key:
```bash
openssl rand -base64 32 | tr -d '/+=' | head -c 43
```

## Usage

### Web Interface

1. Navigate to `http://your-server:8080`
2. Log in with your admin password
3. Use the interface to:
   - **Upload files** - Click "Upload Files" or drag-and-drop
   - **Download files** - Click the download button on any file
   - **Copy link** - Get a direct download URL for sharing
   - **Rename files** - Click the menu (⋮) and select "Rename"
   - **Delete files** - Click the menu (⋮) and select "Delete"

### CLI Tool

Configure the CLI with your API key:
```bash
/opt/glassfile/filemanager config --key YOUR_API_KEY --url http://localhost:8080
```

Available commands:
```bash
# List all files
./filemanager list

# Upload a file
./filemanager upload /path/to/file.pdf

# Download a file
./filemanager download filename.pdf

# Delete a file
./filemanager delete filename.pdf

# Rename a file
./filemanager rename old-name.pdf new-name.pdf

# Get file information
./filemanager info filename.pdf

# Show current configuration
./filemanager config
```

### Direct Download Links

Files are publicly accessible via direct URLs:
```bash
# Download with wget
wget http://your-server:8080/files/document.pdf

# Download with curl
curl -O http://your-server:8080/files/document.pdf
```

## API Reference

All API endpoints return JSON responses:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Authentication

- **Web Interface**: Session-based (login with password)
- **API/CLI**: Header-based (`X-API-Key: your-key`)

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/login` | None | Login with password |
| GET | `/logout` | Session | Logout |
| GET | `/api/files` | Yes | List all files |
| POST | `/api/upload` | Yes | Upload a file |
| DELETE | `/api/files/<name>` | Yes | Delete a file |
| PUT | `/api/files/<name>` | Yes | Rename a file |
| GET | `/api/files/<name>/info` | Yes | Get file metadata |
| GET | `/files/<name>` | None | Download file (public) |
| GET | `/health` | None | Health check |

### Examples

```bash
# List files
curl -H "X-API-Key: YOUR_KEY" http://localhost:8080/api/files

# Upload file
curl -H "X-API-Key: YOUR_KEY" -F "file=@document.pdf" http://localhost:8080/api/upload

# Delete file
curl -X DELETE -H "X-API-Key: YOUR_KEY" http://localhost:8080/api/files/document.pdf

# Rename file
curl -X PUT -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"new_name": "renamed.pdf"}' http://localhost:8080/api/files/document.pdf
```

## Production Deployment

### Systemd Service

The service is managed with systemctl:
```bash
sudo systemctl start glassfile    # Start the service
sudo systemctl stop glassfile     # Stop the service
sudo systemctl restart glassfile  # Restart the service
sudo systemctl status glassfile   # Check status
```

View logs:
```bash
sudo journalctl -u glassfile -f              # Follow logs
sudo tail -f /var/log/glassfile/error.log    # Error log
sudo tail -f /var/log/glassfile/access.log   # Access log
```

### Nginx Reverse Proxy

1. Copy the example configuration:
   ```bash
   sudo cp nginx.conf.example /etc/nginx/sites-available/glassfile
   ```

2. Edit the configuration:
   ```bash
   sudo nano /etc/nginx/sites-available/glassfile
   # Change server_name to your domain
   ```

3. Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/glassfile /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### SSL/HTTPS with Let's Encrypt

1. Install certbot:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. Obtain certificate:
   ```bash
   sudo certbot --nginx -d files.yourdomain.com
   ```

3. Certificate auto-renewal is handled by certbot automatically.

### Firewall Configuration

```bash
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## Security Considerations

### Best Practices

1. **Change default credentials** - Always change the admin password after installation
2. **Use HTTPS** - Set up SSL/TLS for production use
3. **Firewall rules** - Only expose necessary ports
4. **Regular updates** - Keep the system and dependencies updated
5. **IP whitelist** - Consider restricting management access by IP

### Security Features

- **Password hashing** - Passwords are hashed using werkzeug's secure methods
- **Session management** - Secure session cookies with configurable lifetime
- **Security headers** - X-Frame-Options, X-Content-Type-Options, CSP headers
- **Rate limiting** - Nginx configuration includes rate limiting
- **Systemd hardening** - Service runs with restricted privileges:
  - NoNewPrivileges
  - PrivateTmp
  - ProtectSystem=strict
  - ProtectHome=true
  - Memory and CPU limits

### File Upload Security

- File size limits enforced
- Optional extension filtering
- Files stored outside web root
- Filenames sanitized to prevent path traversal

## Troubleshooting

### Service won't start

Check the logs:
```bash
sudo journalctl -u glassfile -n 50
```

Common issues:
- Missing Python dependencies: `sudo /opt/glassfile/venv/bin/pip install -r /opt/glassfile/requirements.txt`
- Permission issues: `sudo chown -R filemanager:filemanager /opt/glassfile`
- Port already in use: Check with `sudo lsof -i :8080`

### Can't log in

1. Verify the password hash in config.yaml
2. Check session_lifetime setting
3. Clear browser cookies and try again

### CLI authentication fails

1. Verify API key in config.yaml matches CLI configuration
2. Check server URL in CLI config: `./filemanager config`
3. Ensure server is running: `curl http://localhost:8080/health`

### File upload fails

1. Check max_file_size in config.yaml
2. Verify directory permissions: `ls -la /opt/glassfile/static/files/`
3. Check available disk space: `df -h`

## Development

### Running locally

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create config.yaml with test credentials

# Run the server
python fileserver.py
```

### Project Structure

```
glassfile/
├── fileserver.py         # Main Flask application
├── filemanager           # CLI management tool
├── config.yaml           # Configuration file
├── requirements.txt      # Python dependencies
├── templates/
│   ├── index.html        # Main interface
│   ├── login.html        # Login page
│   └── error.html        # Error page
├── static/
│   └── files/            # File storage directory
├── fileserver.service    # Systemd service file
├── nginx.conf.example    # Nginx configuration
├── install.sh            # Installation script
├── CLAUDE.md             # Development guide
├── MILESTONES.md         # Development milestones
└── README.md             # This file
```

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- Design inspired by Apple's glassmorphism aesthetic
- Built with Flask, a lightweight Python web framework
- Icons and animations crafted with care for a premium experience
