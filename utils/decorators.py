from functools import wraps
from flask import g, request, session, redirect, url_for, flash

def with_navigation(f):
    """
    Decorator to ensure navigation state is tracked properly.
    This sets the current_path in the Flask g object for templates to use.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.current_path = request.path
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            response = redirect(url_for('user.login'))
            # Add cache control headers
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
            
        if not session['user'].get('is_admin', False):
            flash('You do not have permission to access this page.', 'danger')
            response = redirect(url_for('general.home'))
            # Add cache control headers
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
            
        # Mark session as modified to ensure it stays active
        session.modified = True
        return f(*args, **kwargs)
    return decorated_function 