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
