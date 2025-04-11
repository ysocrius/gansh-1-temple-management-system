from flask import Flask, jsonify, g, session, render_template, request, flash, redirect, url_for
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from config import Config
from datetime import timedelta
import os
import secrets
import logging
from utils.mail import mail, init_mail

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration from Config class
app.config.from_object(Config)

# Function to read maintenance status from file
def load_maintenance_status():
    """Load maintenance mode status from file and apply to app config"""
    try:
        import json
        maintenance_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'maintenance_status.json')
        if os.path.exists(maintenance_file):
            with open(maintenance_file, 'r') as f:
                maintenance_data = json.load(f)
                # Update app config with file data
                app.config["MAINTENANCE_MODE"] = maintenance_data.get("maintenance_mode", False)
                if "end_time" in maintenance_data and maintenance_data["end_time"]:
                    app.config["MAINTENANCE_END_TIME"] = maintenance_data["end_time"]
                
                # Add additional debug logging
                logger.info(f"Loaded maintenance mode status from file: ENABLED={app.config['MAINTENANCE_MODE']}")
                logger.info(f"Maintenance mode end time: {app.config.get('MAINTENANCE_END_TIME')}")
                logger.info(f"Full maintenance data from file: {maintenance_data}")
                
                # Ensure MAINTENANCE_BYPASS_IPS is preserved from config and not overwritten
                logger.info(f"Maintenance bypass IPs: {app.config.get('MAINTENANCE_BYPASS_IPS')}")
                
                return maintenance_data
        else:
            logger.warning(f"Maintenance file not found at {maintenance_file}, using default config settings")
    except Exception as e:
        logger.error(f"Error loading maintenance status: {str(e)}")
    
    # In case of error, ensure maintenance mode is set according to config
    app.config["MAINTENANCE_MODE"] = Config.MAINTENANCE_MODE
    logger.info(f"Using config default for maintenance mode: {app.config['MAINTENANCE_MODE']}")
    return None

# Setup a background thread to periodically verify maintenance mode
def verify_maintenance_mode():
    """Background thread to verify maintenance mode settings are preserved"""
    import time
    import json
    import os
    import datetime
    from database import maintenance_log
    
    while True:
        try:
            # Sleep for 30 seconds between checks
            time.sleep(30)
            
            # Check if maintenance file exists
            maintenance_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'maintenance_status.json')
            if os.path.exists(maintenance_file):
                with open(maintenance_file, 'r') as f:
                    maintenance_data = json.load(f)
                    file_mode = maintenance_data.get("maintenance_mode", False)
                    app_mode = app.config.get("MAINTENANCE_MODE", False)
                    
                    # If there's a mismatch, log it and restore from file
                    if file_mode != app_mode:
                        logger.warning(f"Maintenance mode mismatch detected in background thread: app={app_mode}, file={file_mode}")
                        logger.warning("Restoring maintenance mode from file")
                        
                        # Record the timestamp for logging
                        unix_timestamp = int(time.time())
                        
                        # Check direction of the change (auto-enable or auto-disable)
                        action = "auto_enabled" if file_mode else "auto_disabled"
                        opposite_action = "disabled" if file_mode else "enabled"
                        
                        # Find the last maintenance action to calculate duration
                        try:
                            last_action = maintenance_log.find_one(
                                {"action": opposite_action},
                                sort=[("timestamp_unix", -1)]
                            )
                            
                            duration = None
                            if last_action and "timestamp_unix" in last_action:
                                # Calculate how long the site was in previous state (seconds)
                                duration = unix_timestamp - last_action["timestamp_unix"]
                            
                            # Format duration for display
                            from routes.admin import format_duration
                            formatted_duration = format_duration(duration) if duration else None
                            
                            # Log the automatic change to maintenance_log collection
                            duration_field = "uptime_duration" if action == "auto_enabled" else "downtime_duration"
                            formatted_field = "uptime_formatted" if action == "auto_enabled" else "downtime_formatted"
                            
                            log_entry = {
                                "action": action,
                                "timestamp_unix": unix_timestamp,
                                "timestamp": datetime.datetime.fromtimestamp(unix_timestamp),
                                "admin_email": "system",  # Indicate this was automatic
                                "ip_address": "127.0.0.1",
                                "user_agent": "maintenance_monitor",
                                "source": "background_verification",
                                duration_field: duration,
                                formatted_field: formatted_duration
                            }
                            
                            maintenance_log.insert_one(log_entry)
                            logger.info(f"Automatic maintenance mode change logged: {action}")
                            logger.info(f"Log entry: {log_entry}")
                        except Exception as e:
                            logger.error(f"Error logging automatic maintenance change: {str(e)}")
                        
                        # Restore the maintenance mode from file
                        app.config["MAINTENANCE_MODE"] = file_mode
                        logger.info(f"Maintenance mode restored to: {app.config['MAINTENANCE_MODE']}")
                    else:
                        logger.debug("Maintenance mode verification: status matches file configuration")
        except Exception as e:
            logger.error(f"Error in maintenance mode verification thread: {str(e)}")

# Load maintenance status at startup
maintenance_data = load_maintenance_status()

# Start background verification thread
import threading
maintenance_thread = threading.Thread(target=verify_maintenance_mode, daemon=True)
maintenance_thread.start()
logger.info("Started maintenance mode verification background thread")

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Manually configure CSRF tokens to use a different approach
app.config.update(
    # CSRF Security - disable for testing
    WTF_CSRF_ENABLED=False,  # Disable CSRF for testing/debugging
    
    # Session
    SESSION_TYPE='filesystem',
    SESSION_COOKIE_NAME='temple_session',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,  # Set to True in production
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_USE_SIGNER=True,  # Sign the session cookie for security
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),  # Extended lifetime
    SESSION_FILE_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session'),
    SESSION_FILE_THRESHOLD=500,  # Maximum number of sessions stored in filesystem
    SESSION_REFRESH_EACH_REQUEST=True,  # Update session on each request
    SESSION_PERMANENT=True,  # Make all sessions permanent by default
    
    # Debug
    DEBUG=True
)

# Ensure session directory exists
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# Initialize extensions in the correct order
Session(app)
init_mail(app)

# Disable CSRF protection during testing/development to resolve token issues
csrf.exempt('user.forgot_password')
csrf.exempt('user.verify_otp')  
csrf.exempt('user.reset_password')
csrf.exempt('user.verify_registration_otp')

# Log configuration
logger.debug("App configuration loaded")
logger.debug("Session directory: %s", app.config['SESSION_FILE_DIR'])
logger.debug("Secret key set: %s", bool(app.config['SECRET_KEY']))
logger.debug("Session interface: %s", app.session_interface)
# Log mail configuration
logger.debug("Mail server: %s", app.config['MAIL_SERVER'])
logger.debug("Mail username: %s", app.config['MAIL_USERNAME'])
logger.debug("Mail default sender: %s", app.config['MAIL_DEFAULT_SENDER'])

# Request logging middleware
@app.before_request
def log_request_info():
    """Log request information and ensure session is working"""
    logger.debug('Headers: %s', dict(request.headers))
    logger.debug('Method: %s, Path: %s', request.method, request.path)
    logger.debug('Session: %s', dict(session))
    
    # Make session permanent by default and refresh cookie
    session.permanent = True
    session.modified = True
    
    # Define password reset routes that don't require authentication
    password_reset_paths = ['/user/forgot_password', '/user/verify-otp', '/user/reset_password', '/user/verify-registration-otp']
    
    # Check if the current path is a password reset path
    is_password_reset = request.path in password_reset_paths
    
    # Set user authentication flag for templates, considering password reset exceptions
    g.is_authenticated = 'user' in session
    
    # Special case for password reset flow - if email is in session, treat as special flow
    if not g.is_authenticated and is_password_reset and session.get('email'):
        logger.debug('Password reset flow detected, allowing access without auth')
        g.is_password_reset = True
    else:
        g.is_password_reset = False
    
    g.user_data = session.get('user', {}) if g.is_authenticated else {}
    
    # If user is authenticated, mark session as modified on every request
    # This helps keep the session alive and prevents timeouts
    if g.is_authenticated:
        session.modified = True
        logger.debug('User authenticated, session marked as modified')
    
    # Check if session is working
    if not hasattr(g, '_session_check'):
        test_key = '_session_test'
        session[test_key] = True
        session.modified = True
        g._session_check = session.get(test_key)
        session.pop(test_key, None)
        
        if not g._session_check:
            logger.error('Session test failed!')

# Maintenance mode middleware
@app.before_request
def check_maintenance_mode():
    """Check if the application is in maintenance mode and handle accordingly"""
    # Skip this middleware for OPTIONS requests (for CORS preflight)
    if request.method == 'OPTIONS':
        return None
        
    # Skip check if maintenance mode is not enabled
    if not app.config.get('MAINTENANCE_MODE', False):
        return None
        
    # Print for debugging - remove in production
    logger.debug(f'Maintenance mode check for path: {request.path}, IP: {request.remote_addr}')
    
    # Allow bypassing by specific IPs (e.g., admin IPs)
    client_ip = request.remote_addr
    if client_ip in app.config.get('MAINTENANCE_BYPASS_IPS', []):
        logger.debug(f'Maintenance mode bypass for IP: {client_ip}')
        return None
        
    # Check if the path should bypass maintenance mode
    bypass_paths = app.config.get('MAINTENANCE_BYPASS_PATHS', [])
    for path in bypass_paths:
        if request.path.startswith(path):
            logger.debug(f'Maintenance mode bypass for path: {request.path} (matches {path})')
            return None
            
    # Check if the user is an admin
    if 'admin' in session and session['admin'] == True:
        logger.debug('Maintenance mode bypass for admin user')
        return None
            
    # If we get here, show the maintenance page
    logger.info(f'Maintenance mode active, redirecting {request.path} to maintenance page')
    maintenance_end_time = app.config.get('MAINTENANCE_END_TIME', '24 hours')
    return render_template('user/maintainence.html', completion_time=maintenance_end_time), 503

@app.after_request
def after_request(response):
    logger.debug('Response Status: %s', response.status)
    
    # Define password reset routes that don't require authentication
    password_reset_paths = ['/user/forgot_password', '/user/verify-otp', '/user/reset_password', '/user/verify-registration-otp']
    
    # Check if this is a password reset path
    is_password_reset = request.path in password_reset_paths
    
    # Add cache control headers for authenticated routes, password reset routes, and all admin routes
    if g.get('is_authenticated', False) or g.get('is_password_reset', False) or '/admin/' in request.path or is_password_reset:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    
    # For paths with testimonials/admin ensure to set strong cache control
    if '/testimonials/admin/' in request.path:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
    return response

# Now import routes after app and mail are initialized
from routes.user import user_bp  # Import user routes
from routes.admin import admin_bp
from routes.donations import donations_bp
from routes.donation_management import donation_management_bp
from routes.events import events_bp
from routes.general_admin import general_admin_bp
from routes.general import general_bp
from routes.seva import sevas_bp
from routes.user_seva import seva_bp  # Ensure correct import
from routes.testimonials import testimonials as testimonials_bp  # Import testimonials blueprint
from database import client  # Ensure MongoDB is initialized

# Add a test route directly to the Flask app
@app.route('/test')
def test_route():
    return jsonify({"status": "success", "message": "Flask server is working"})

# Add test route for checking maintenance mode
@app.route('/test-maintenance')
def test_maintenance():
    """Route to test maintenance mode status"""
    maintenance_mode = app.config.get("MAINTENANCE_MODE", False)
    maintenance_end_time = app.config.get("MAINTENANCE_END_TIME", "24 hours")
    bypass_ips = app.config.get("MAINTENANCE_BYPASS_IPS", ["127.0.0.1"])
    bypass_paths = app.config.get("MAINTENANCE_BYPASS_PATHS", [])
    
    # Check if we're in maintenance mode
    if maintenance_mode:
        # If this endpoint is being accessed, it means either:
        # 1. We're not in maintenance mode
        # 2. The user is an admin
        # 3. The user's IP is in the bypass list
        # 4. This path is in the bypass list
        return jsonify({
            "maintenance_mode": True,
            "message": "Maintenance mode is ACTIVE but you're seeing this because you're bypassing it",
            "end_time": maintenance_end_time,
            "bypass_ips": bypass_ips,
            "bypass_paths": bypass_paths,
            "user_ip": request.remote_addr,
            "is_admin": 'admin' in session and session['admin'] == True
        })
    else:
        return jsonify({
            "maintenance_mode": False,
            "message": "Maintenance mode is NOT active",
            "your_ip": request.remote_addr
        })

# Add authentication check endpoint
@app.route('/check-auth')
def check_auth():
    """Check if the user is currently authenticated"""
    try:
        is_authenticated = 'user' in session
        return jsonify({
            "is_authenticated": is_authenticated,
            "user": session.get('user', {}) if is_authenticated else None
        })
    except Exception as e:
        app.logger.error(f"Error checking authentication: {str(e)}")
        return jsonify({"is_authenticated": False, "error": "Error checking authentication status"}), 500

# Inject current URL path into template context for active navigation
@app.context_processor
def inject_current_path():
    # Get user data from session
    user = session.get('user', None)
    
    # Create user_data from user session if available
    user_data = None
    if user:
        user_data = user
    
    return {
        'current_path': request.path,
        'is_authenticated': g.get('is_authenticated', False),
        'is_password_reset': g.get('is_password_reset', False),
        'user': user,
        'user_data': user_data  # Add user_data to context
    }

# Set current path for all requests
@app.before_request
def before_request():
    # Log request information
    app.logger.debug(f"Request: {request.method} {request.path}")
    app.logger.debug(f"Session at before_request: {dict(session)}")
    
    # Check if session is working
    if 'visits' not in session:
        session['visits'] = 0
    session['visits'] = session.get('visits', 0) + 1
    
    # Define password reset paths that don't require authentication
    password_reset_paths = [
        '/user/forgot_password',
        '/user/verify-otp',
        '/user/reset_password',
        '/user/verify-registration-otp'
    ]
    
    # Check if current path is a password reset path
    is_password_reset_path = request.path in password_reset_paths
    
    # Set user authentication flag for templates
    is_authenticated = 'user' in session
    
    # Special case for password reset flow (has email in session but not logged in)
    if not is_authenticated and 'email' in session and is_password_reset_path:
        app.logger.debug(f"Password reset flow detected for path: {request.path}")
        # Mark as password reset flow so it won't be redirected
        g.is_password_reset = True
    else:
        g.is_password_reset = False
    
    g.is_authenticated = is_authenticated
    
    app.logger.debug(f"Authentication status: {g.is_authenticated}, Password reset: {g.is_password_reset}")
    
    # If user is authenticated, mark session as modified on every request
    # This helps keep the session alive and prevents timeouts
    if g.is_authenticated:
        session.modified = True
        logger.debug('User authenticated, session marked as modified')
    
    # Check if session is working
    if not hasattr(g, '_session_check'):
        test_key = '_session_test'
        session[test_key] = True
        session.modified = True
        g._session_check = session.get(test_key)
        session.pop(test_key, None)
        
        if not g._session_check:
            logger.error('Session test failed!')

# Add middleware to check authentication and redirect to login if needed
@app.before_request
def check_auth_middleware():
    # Skip for static files
    if request.path.startswith('/static'):
        return None
        
    # Define paths that don't require authentication
    public_paths = [
        '/',
        '/user/login',
        '/user/register',
        '/user/google_login',    # Add Google login
        '/user/google_callback', # Add Google callback
        '/general-sevas',
        '/history',
        '/donations',
        '/events',
        '/contact',
        '/about',
        '/temple-history',
        '/pooja-timings',
        '/gallery',
        '/e-hundi',
        '/admin/login'
    ]
    
    # Define password reset paths
    password_reset_paths = [
        '/user/forgot_password',
        '/user/verify-otp',
        '/user/reset_password',
        '/user/verify-registration-otp'
    ]
    
    # Check if path is a password reset path
    is_password_reset_path = request.path in password_reset_paths
    
    # Skip authentication check for public paths, password reset paths with email in session,
    # or any path if the user is authenticated
    if (request.path in public_paths or 
            (is_password_reset_path and 'email' in session) or 
            g.is_authenticated or 
            g.is_password_reset):
        app.logger.debug(f"Skipping auth check for {request.path} - Public or authenticated or password reset")
        return None
        
    # For protected user paths that aren't password reset paths, redirect to login if not authenticated
    if request.path.startswith('/user/') and not g.is_authenticated and not is_password_reset_path:
        app.logger.debug(f"Redirecting to login for protected path: {request.path}")
        flash('Please log in to access this page.', 'warning')
        # Include next parameter in the redirect URL
        response = redirect(url_for('user.login', next=request.path))
        
        # Add cache control headers to prevent caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
        
    # For admin paths, we'll use our decorator from admin.py

# ✅ Register Blueprints
app.register_blueprint(general_bp)
app.register_blueprint(general_admin_bp, url_prefix="/admin/general")  
app.register_blueprint(events_bp, url_prefix="/admin")
app.register_blueprint(seva_bp, url_prefix="/seva")
app.register_blueprint(sevas_bp, url_prefix="/sevas")
app.register_blueprint(admin_bp, url_prefix="/admin")  
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(donations_bp, url_prefix="/donations")
app.register_blueprint(donation_management_bp, url_prefix="/admin/donations")
app.register_blueprint(testimonials_bp)  # Register testimonials blueprint without prefix to allow both /testimonials and /admin paths

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

# Ensure this route exists and is accessible
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Your login logic here
    return render_template('user/login.html')

# Add a route to check CSRF token status
@app.route('/check-csrf')
def check_csrf():
    """Route to check CSRF token and session state"""
    try:
        csrf_token = csrf._get_csrf_token()
        return jsonify({
            "csrf_working": bool(csrf_token),
            "csrf_token": csrf_token,
            "session": {key: session[key] for key in session if key != 'csrf_token'},
            "has_csrf_in_session": 'csrf_token' in session
        })
    except Exception as e:
        app.logger.error(f"Error checking CSRF: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
