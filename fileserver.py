#!/usr/bin/env python3
"""
Glassmorphic File Manager - Flask Backend
A stunning, secure file hosting solution with Apple-inspired design.
"""

import os
import re
import logging
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import yaml
from flask import (
    Flask, request, jsonify, session, redirect, url_for,
    render_template, send_from_directory, abort
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fileserver.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)


def load_config(config_path: str = 'config.yaml') -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration: {e}")
        raise


def validate_config(config: dict) -> bool:
    """Validate configuration values."""
    required_keys = ['server', 'storage', 'security']
    for key in required_keys:
        if key not in config:
            logger.error(f"Missing required configuration key: {key}")
            return False

    # Validate storage directory exists
    storage_dir = config['storage']['directory']
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir, exist_ok=True)
        logger.info(f"Created storage directory: {storage_dir}")

    # Validate password hash exists
    if not config['security'].get('admin_password_hash'):
        logger.error("No admin password hash configured")
        return False

    return True


# Load configuration
config = load_config()
if not validate_config(config):
    raise ValueError("Invalid configuration")

# Configure Flask app
app.secret_key = secrets.token_hex(32)
app.config['SESSION_COOKIE_SECURE'] = not config['server'].get('debug', False)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
    seconds=config['security'].get('session_lifetime', 3600)
)
app.config['MAX_CONTENT_LENGTH'] = config['storage'].get('max_file_size', 100 * 1024 * 1024)

# Storage configuration
STORAGE_DIR = Path(config['storage']['directory']).resolve()
ALLOWED_EXTENSIONS = config['storage'].get('allowed_extensions')


# =============================================================================
# Security Headers Middleware
# =============================================================================

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


# =============================================================================
# Authentication Decorators
# =============================================================================

def check_ip_whitelist() -> bool:
    """Check if the client IP is in the whitelist."""
    whitelist = config['security'].get('ip_whitelist', [])
    if not whitelist:
        return True

    client_ip = request.remote_addr
    return client_ip in whitelist


def require_login(f):
    """Decorator for routes that require web authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_ip_whitelist():
            logger.warning(f"IP whitelist rejection: {request.remote_addr}")
            abort(403)

        if not session.get('authenticated'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'data': None,
                    'error': 'Authentication required'
                }), 401
            return redirect(url_for('login_page'))

        # Check session timeout
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity = datetime.fromisoformat(last_activity)
            timeout = config['security'].get('session_lifetime', 3600)
            if datetime.now() - last_activity > timedelta(seconds=timeout):
                session.clear()
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'data': None,
                        'error': 'Session expired'
                    }), 401
                return redirect(url_for('login_page'))

        # Update last activity
        session['last_activity'] = datetime.now().isoformat()
        return f(*args, **kwargs)
    return decorated_function


def require_api_key(f):
    """Decorator for routes that require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_ip_whitelist():
            logger.warning(f"IP whitelist rejection: {request.remote_addr}")
            abort(403)

        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'success': False,
                'data': None,
                'error': 'API key required'
            }), 401

        valid_keys = config['security'].get('api_keys', [])
        if api_key not in valid_keys:
            logger.warning(f"Invalid API key attempt from {request.remote_addr}")
            return jsonify({
                'success': False,
                'data': None,
                'error': 'Invalid API key'
            }), 401

        return f(*args, **kwargs)
    return decorated_function


def require_auth(f):
    """Decorator that accepts either session or API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_ip_whitelist():
            logger.warning(f"IP whitelist rejection: {request.remote_addr}")
            abort(403)

        # Check API key first
        api_key = request.headers.get('X-API-Key')
        if api_key:
            valid_keys = config['security'].get('api_keys', [])
            if api_key in valid_keys:
                return f(*args, **kwargs)
            return jsonify({
                'success': False,
                'data': None,
                'error': 'Invalid API key'
            }), 401

        # Fall back to session authentication
        if session.get('authenticated'):
            last_activity = session.get('last_activity')
            if last_activity:
                last_activity = datetime.fromisoformat(last_activity)
                timeout = config['security'].get('session_lifetime', 3600)
                if datetime.now() - last_activity > timedelta(seconds=timeout):
                    session.clear()
                    return jsonify({
                        'success': False,
                        'data': None,
                        'error': 'Session expired'
                    }), 401
            session['last_activity'] = datetime.now().isoformat()
            return f(*args, **kwargs)

        return jsonify({
            'success': False,
            'data': None,
            'error': 'Authentication required'
        }), 401
    return decorated_function


# =============================================================================
# File Operations Utilities
# =============================================================================

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent directory traversal and other issues."""
    # Use werkzeug's secure_filename first
    safe_name = secure_filename(filename)

    # Additional sanitization
    safe_name = re.sub(r'[<>:"/\\|?*]', '', safe_name)
    safe_name = safe_name.strip('. ')

    if not safe_name:
        raise ValueError("Invalid filename")

    return safe_name


def is_allowed_extension(filename: str) -> bool:
    """Check if the file extension is allowed."""
    if ALLOWED_EXTENSIONS is None:
        return True

    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def get_file_metadata(filepath: Path) -> dict:
    """Get metadata for a file."""
    stat = filepath.stat()
    return {
        'name': filepath.name,
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'extension': filepath.suffix.lower(),
        'url': f"/files/{filepath.name}"
    }


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_relative_time(dt: datetime) -> str:
    """Convert datetime to relative time string."""
    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        return dt.strftime('%b %d, %Y')


# =============================================================================
# Error Handlers
# =============================================================================

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Bad request'
        }), 400
    return render_template('error.html', code=400, message='Bad Request'), 400


@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors."""
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Unauthorized'
        }), 401
    return redirect(url_for('login_page'))


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors."""
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Forbidden'
        }), 403
    return render_template('error.html', code=403, message='Forbidden'), 403


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Not found'
        }), 404
    return render_template('error.html', code=404, message='Not Found'), 404


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 Request Entity Too Large errors."""
    max_size = format_file_size(config['storage'].get('max_file_size', 100 * 1024 * 1024))
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'data': None,
            'error': f'File too large. Maximum size is {max_size}'
        }), 413
    return render_template('error.html', code=413, message=f'File too large. Maximum size is {max_size}'), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    logger.error(f"Internal server error: {error}")
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Internal server error'
        }), 500
    return render_template('error.html', code=500, message='Internal Server Error'), 500


# =============================================================================
# Authentication Routes
# =============================================================================

@app.route('/login', methods=['GET'])
def login_page():
    """Render login page."""
    if session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    """Handle login submission."""
    if not request.is_json:
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Content-Type must be application/json'
        }), 400

    data = request.get_json()
    password = data.get('password', '')

    password_hash = config['security'].get('admin_password_hash', '')
    if check_password_hash(password_hash, password):
        # Regenerate session ID on login for security
        session.clear()
        session['authenticated'] = True
        session['last_activity'] = datetime.now().isoformat()
        session.permanent = True
        logger.info(f"Successful login from {request.remote_addr}")
        return jsonify({
            'success': True,
            'data': {'message': 'Login successful'},
            'error': None
        })

    logger.warning(f"Failed login attempt from {request.remote_addr}")
    return jsonify({
        'success': False,
        'data': None,
        'error': 'Invalid password'
    }), 401


@app.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.clear()
    logger.info(f"Logout from {request.remote_addr}")
    return redirect(url_for('login_page'))


# =============================================================================
# Web Interface Routes
# =============================================================================

@app.route('/')
@require_login
def index():
    """Render main interface."""
    return render_template('index.html')


# =============================================================================
# API Routes - File Operations
# =============================================================================

@app.route('/api/files', methods=['GET'])
@require_auth
def list_files():
    """List all files with metadata."""
    try:
        files = []
        for filepath in STORAGE_DIR.iterdir():
            if filepath.is_file():
                metadata = get_file_metadata(filepath)
                # Add human-readable formats
                metadata['size_formatted'] = format_file_size(metadata['size'])
                modified_dt = datetime.fromisoformat(metadata['modified'])
                metadata['modified_relative'] = get_relative_time(modified_dt)
                files.append(metadata)

        # Sort by modification time, newest first
        files.sort(key=lambda x: x['modified'], reverse=True)

        return jsonify({
            'success': True,
            'data': {
                'files': files,
                'total': len(files)
            },
            'error': None
        })
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Failed to list files'
        }), 500


@app.route('/api/upload', methods=['POST'])
@require_auth
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'data': None,
            'error': 'No file provided'
        }), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'success': False,
            'data': None,
            'error': 'No file selected'
        }), 400

    try:
        filename = sanitize_filename(file.filename)
    except ValueError as e:
        return jsonify({
            'success': False,
            'data': None,
            'error': str(e)
        }), 400

    if not is_allowed_extension(filename):
        return jsonify({
            'success': False,
            'data': None,
            'error': 'File type not allowed'
        }), 400

    # Handle duplicate filenames
    filepath = STORAGE_DIR / filename
    if filepath.exists():
        # Add number suffix to filename
        base = filepath.stem
        ext = filepath.suffix
        counter = 1
        while filepath.exists():
            filename = f"{base}_{counter}{ext}"
            filepath = STORAGE_DIR / filename
            counter += 1

    try:
        file.save(filepath)
        metadata = get_file_metadata(filepath)
        metadata['size_formatted'] = format_file_size(metadata['size'])
        modified_dt = datetime.fromisoformat(metadata['modified'])
        metadata['modified_relative'] = get_relative_time(modified_dt)

        logger.info(f"File uploaded: {filename} from {request.remote_addr}")
        return jsonify({
            'success': True,
            'data': metadata,
            'error': None
        })
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Failed to upload file'
        }), 500


@app.route('/api/files/<filename>', methods=['DELETE'])
@require_auth
def delete_file(filename: str):
    """Delete a file."""
    try:
        safe_filename = sanitize_filename(filename)
    except ValueError:
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Invalid filename'
        }), 400

    filepath = STORAGE_DIR / safe_filename
    if not filepath.exists():
        return jsonify({
            'success': False,
            'data': None,
            'error': 'File not found'
        }), 404

    # Ensure we're not deleting outside storage directory
    if not filepath.resolve().is_relative_to(STORAGE_DIR):
        logger.warning(f"Path traversal attempt: {filename} from {request.remote_addr}")
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Invalid path'
        }), 400

    try:
        filepath.unlink()
        logger.info(f"File deleted: {safe_filename} from {request.remote_addr}")
        return jsonify({
            'success': True,
            'data': {'message': f'File {safe_filename} deleted'},
            'error': None
        })
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Failed to delete file'
        }), 500


@app.route('/api/files/<filename>', methods=['PUT'])
@require_auth
def rename_file(filename: str):
    """Rename a file."""
    if not request.is_json:
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Content-Type must be application/json'
        }), 400

    data = request.get_json()
    new_name = data.get('new_name', '')

    try:
        safe_old_name = sanitize_filename(filename)
        safe_new_name = sanitize_filename(new_name)
    except ValueError:
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Invalid filename'
        }), 400

    if not is_allowed_extension(safe_new_name):
        return jsonify({
            'success': False,
            'data': None,
            'error': 'File type not allowed'
        }), 400

    old_path = STORAGE_DIR / safe_old_name
    new_path = STORAGE_DIR / safe_new_name

    if not old_path.exists():
        return jsonify({
            'success': False,
            'data': None,
            'error': 'File not found'
        }), 404

    if new_path.exists():
        return jsonify({
            'success': False,
            'data': None,
            'error': 'A file with that name already exists'
        }), 409

    # Ensure we're not operating outside storage directory
    if not old_path.resolve().is_relative_to(STORAGE_DIR):
        logger.warning(f"Path traversal attempt: {filename} from {request.remote_addr}")
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Invalid path'
        }), 400

    try:
        old_path.rename(new_path)
        metadata = get_file_metadata(new_path)
        metadata['size_formatted'] = format_file_size(metadata['size'])
        modified_dt = datetime.fromisoformat(metadata['modified'])
        metadata['modified_relative'] = get_relative_time(modified_dt)

        logger.info(f"File renamed: {safe_old_name} -> {safe_new_name} from {request.remote_addr}")
        return jsonify({
            'success': True,
            'data': metadata,
            'error': None
        })
    except Exception as e:
        logger.error(f"Error renaming file: {e}")
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Failed to rename file'
        }), 500


@app.route('/api/files/<filename>/info', methods=['GET'])
@require_auth
def file_info(filename: str):
    """Get detailed file information."""
    try:
        safe_filename = sanitize_filename(filename)
    except ValueError:
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Invalid filename'
        }), 400

    filepath = STORAGE_DIR / safe_filename
    if not filepath.exists():
        return jsonify({
            'success': False,
            'data': None,
            'error': 'File not found'
        }), 404

    try:
        metadata = get_file_metadata(filepath)
        metadata['size_formatted'] = format_file_size(metadata['size'])
        modified_dt = datetime.fromisoformat(metadata['modified'])
        created_dt = datetime.fromisoformat(metadata['created'])
        metadata['modified_relative'] = get_relative_time(modified_dt)
        metadata['created_relative'] = get_relative_time(created_dt)

        return jsonify({
            'success': True,
            'data': metadata,
            'error': None
        })
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Failed to get file information'
        }), 500


# =============================================================================
# Public File Access (No Authentication Required)
# =============================================================================

@app.route('/files/<filename>')
def download_file(filename: str):
    """Serve file for download (wget-compatible, no auth required)."""
    try:
        safe_filename = sanitize_filename(filename)
    except ValueError:
        abort(404)

    filepath = STORAGE_DIR / safe_filename
    if not filepath.exists():
        abort(404)

    # Ensure we're not serving files outside storage directory
    if not filepath.resolve().is_relative_to(STORAGE_DIR):
        logger.warning(f"Path traversal attempt in download: {filename}")
        abort(404)

    logger.info(f"File download: {safe_filename} from {request.remote_addr}")
    return send_from_directory(
        STORAGE_DIR,
        safe_filename,
        as_attachment=True
    )


# =============================================================================
# Health Check
# =============================================================================

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'storage_dir': str(STORAGE_DIR),
        'storage_writable': os.access(STORAGE_DIR, os.W_OK)
    })


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    # Ensure storage directory exists
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    host = config['server'].get('host', '0.0.0.0')
    port = config['server'].get('port', 8080)
    debug = config['server'].get('debug', False)

    logger.info(f"Starting Glassmorphic File Manager on {host}:{port}")
    logger.info(f"Storage directory: {STORAGE_DIR}")
    logger.info(f"Debug mode: {debug}")

    app.run(host=host, port=port, debug=debug)
