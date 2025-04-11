from flask import Blueprint, render_template, request, redirect, url_for, session, make_response, flash
from database import user_collection, seva_collection, donations_collection, admin_log, maintenance_log
from bson.objectid import ObjectId
import datetime
import json
import os
import sys
import random
import time
import logging
from flask_mail import Message
from utils.mail import mail
import secrets
import hashlib
from werkzeug.security import safe_str_cmp

# Configure logger
logger = logging.getLogger(__name__)

# Add reference to donation_goals_collection
from database import db
donation_goals_collection = db.donation_goals

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Admin email configuration - Update this with your actual admin email
ADMIN_EMAIL = "yeshwanthcr108@gmail.com"

# Create a dictionary to store valid login tokens and their expiration times
login_tokens = {}

# Track invalid token attempts to prevent brute force attacks
invalid_token_attempts = {}
INVALID_TOKEN_THRESHOLD = 5  # Maximum invalid attempts before temporary ban
INVALID_TOKEN_BAN_DURATION = 15  # Ban duration in minutes

def generate_secure_token():
    """Generate a secure random 64-bit token for admin login URL"""
    # Generate a random token using secrets module (cryptographically secure)
    token = secrets.token_hex(32)  # 32 bytes = 64 hex chars
    
    # Store token with expiration time (20 minutes from now)
    expiration = datetime.datetime.now() + datetime.timedelta(minutes=20)
    login_tokens[token] = expiration
    
    # Clean up expired tokens
    cleanup_expired_tokens()
    
    logger.info(f"Generated new admin login token (expires in 20 minutes)")
    return token

def is_ip_banned(ip_address):
    """Check if an IP address is temporarily banned due to too many invalid token attempts"""
    if ip_address in invalid_token_attempts:
        attempts = invalid_token_attempts[ip_address]["attempts"]
        last_attempt = invalid_token_attempts[ip_address]["timestamp"]
        ban_expiry = last_attempt + datetime.timedelta(minutes=INVALID_TOKEN_BAN_DURATION)
        
        # Check if ban has expired
        if datetime.datetime.now() > ban_expiry:
            # Reset attempts after ban period
            invalid_token_attempts[ip_address]["attempts"] = 0
            return False
        
        # If attempts exceed threshold, IP is banned
        if attempts >= INVALID_TOKEN_THRESHOLD:
            return True
    
    return False

def record_invalid_token_attempt(ip_address):
    """Record an invalid token attempt and return whether the IP is now banned"""
    current_time = datetime.datetime.now()
    
    if ip_address not in invalid_token_attempts:
        invalid_token_attempts[ip_address] = {
            "attempts": 1,
            "timestamp": current_time
        }
    else:
        # Check if we should reset counter due to time elapsed
        last_attempt = invalid_token_attempts[ip_address]["timestamp"]
        if current_time > last_attempt + datetime.timedelta(minutes=INVALID_TOKEN_BAN_DURATION):
            # Reset after ban duration
            invalid_token_attempts[ip_address] = {
                "attempts": 1,
                "timestamp": current_time
            }
        else:
            # Increment attempts
            invalid_token_attempts[ip_address]["attempts"] += 1
            invalid_token_attempts[ip_address]["timestamp"] = current_time
    
    # Log attempt
    attempts = invalid_token_attempts[ip_address]["attempts"]
    logger.warning(f"Invalid token attempt from IP: {ip_address}, Attempts: {attempts}/{INVALID_TOKEN_THRESHOLD}")
    
    # Add to admin log
    if attempts >= INVALID_TOKEN_THRESHOLD:
        admin_log.insert_one({
            "action": "ip_temporarily_banned",
            "ip_address": ip_address,
            "timestamp": current_time,
            "reason": f"Exceeded invalid token attempts: {attempts}",
            "ban_duration_minutes": INVALID_TOKEN_BAN_DURATION
        })
        logger.warning(f"IP temporarily banned due to invalid token attempts: {ip_address}")
        return True
    
    return False

def cleanup_expired_tokens():
    """Remove expired tokens from the login_tokens dictionary"""
    current_time = datetime.datetime.now()
    
    # Clean up expired login tokens
    expired_tokens = [t for t, exp in login_tokens.items() if exp < current_time]
    for t in expired_tokens:
        login_tokens.pop(t, None)
    
    if expired_tokens:
        logger.info(f"Cleaned up {len(expired_tokens)} expired login tokens")
    
    # Clean up expired invalid attempt records
    expired_attempts = []
    for ip, data in invalid_token_attempts.items():
        last_attempt = data["timestamp"]
        # If the last attempt was more than twice the ban duration ago, remove the record
        if current_time > last_attempt + datetime.timedelta(minutes=INVALID_TOKEN_BAN_DURATION * 2):
            expired_attempts.append(ip)
    
    # Remove expired attempt records
    for ip in expired_attempts:
        invalid_token_attempts.pop(ip, None)
    
    if expired_attempts:
        logger.info(f"Cleaned up {len(expired_attempts)} expired IP ban records")
    
    # Log total active tokens and banned IPs for monitoring
    logger.debug(f"Active login tokens: {len(login_tokens)}")
    banned_ips = sum(1 for ip, data in invalid_token_attempts.items() 
                     if data["attempts"] >= INVALID_TOKEN_THRESHOLD and 
                     current_time <= data["timestamp"] + datetime.timedelta(minutes=INVALID_TOKEN_BAN_DURATION))
    logger.debug(f"Currently banned IPs: {banned_ips}")

# Start a background thread to periodically clean up expired tokens
import threading
def token_cleanup_thread():
    """Background thread to periodically clean up expired tokens"""
    import time
    while True:
        try:
            # Sleep for 5 minutes between cleanups
            time.sleep(300)
            cleanup_expired_tokens()
        except Exception as e:
            logger.error(f"Error in token cleanup thread: {str(e)}")

# Start the token cleanup thread when the app starts
cleanup_thread = threading.Thread(target=token_cleanup_thread, daemon=True)
cleanup_thread.start()
logger.info("Started token cleanup background thread")

# Helper function to format duration in seconds to human-readable format
def format_duration(seconds):
    """Format duration in seconds to a human-readable string (days, hours, minutes, seconds)"""
    if seconds is None:
        return None
        
    days = seconds // (24 * 3600)
    seconds %= (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    
    parts = []
    if days > 0:
        parts.append(f"{int(days)}d")
    if hours > 0 or days > 0:
        parts.append(f"{int(hours)}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{int(minutes)}m")
    parts.append(f"{int(seconds)}s")
    
    return " ".join(parts)

# Authentication middleware for admin routes
@admin_bp.before_request
def require_admin():
    # Skip auth check for login page and get-otp endpoints
    if request.endpoint in ["admin.login", "admin.login_with_token", "admin.login_redirect", "admin.get_otp"]:
        return

    # Check if user is logged in and is an admin
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login_redirect"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response

@admin_bp.after_request
def add_cache_headers(response):
    """Add cache control headers to all admin routes"""
    # Check if the user is authenticated as admin
    if session.get("admin") == True:
        # Add cache control headers to prevent caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

@admin_bp.route("/login-redirect")
def login_redirect():
    """Generate a secure token and redirect to the tokenized login URL"""
    # Check if IP is currently banned
    client_ip = request.remote_addr
    if is_ip_banned(client_ip):
        flash("Too many invalid access attempts. Please try again later.", "danger")
        return redirect(url_for("general.home"))
    
    token = generate_secure_token()
    secure_url = url_for("admin.login_with_token", token=token)
    return redirect(secure_url)

@admin_bp.route("/login/<token>", methods=["GET", "POST"])
def login_with_token(token):
    """Admin Login Page with Token Verification and OTP Verification"""
    # Check if IP is currently banned
    client_ip = request.remote_addr
    if is_ip_banned(client_ip):
        flash("Too many invalid access attempts. Please try again later.", "danger")
        return redirect(url_for("general.home"))
    
    # Verify token is valid and not expired
    current_time = datetime.datetime.now()
    if token not in login_tokens or login_tokens[token] < current_time:
        # Invalid or expired token
        logger.warning(f"Invalid or expired admin login token attempted: {token[:10]}...")
        flash("Invalid or expired login link. Please use the Admin Login button to access the login page.", "danger")
        
        # Record invalid attempt
        is_banned = record_invalid_token_attempt(client_ip)
        if is_banned:
            flash(f"Too many invalid attempts. Access temporarily restricted for {INVALID_TOKEN_BAN_DURATION} minutes.", "danger")
        
        return redirect(url_for("general.home"))
    
    # Token is valid, proceed with normal login logic
    if request.method == "POST":
        entered_otp = request.form.get("otp")
        
        # Find active OTP in the database
        otp_record = admin_log.find_one({
            "email": ADMIN_EMAIL,
            "otp": entered_otp,
            "expires_at": {"$gt": datetime.datetime.now()},
            "is_used": False
        })
        
        if otp_record:
            # Mark OTP as used
            admin_log.update_one(
                {"_id": otp_record["_id"]},
                {"$set": {
                    "is_used": True,
                    "used_at": datetime.datetime.now()
                }}
            )
            
            # Set admin session
            session["admin"] = True
            if "user" not in session:
                session["user"] = {}
            session["user"]["is_admin"] = True
            
            # Add login audit
            admin_log.insert_one({
                "email": ADMIN_EMAIL,
                "action": "login_success",
                "timestamp": datetime.datetime.now(),
                "ip_address": request.remote_addr,
                "user_agent": request.user_agent.string
            })
            
            # Remove used token
            login_tokens.pop(token, None)
            
            flash("Login successful! Welcome to the admin panel.", "success")
            return redirect(url_for("general_admin.admin_dashboard"))
        else:
            # Check if OTP exists but is expired
            expired_otp = admin_log.find_one({
                "email": ADMIN_EMAIL,
                "otp": entered_otp,
                "expires_at": {"$lte": datetime.datetime.now()},
                "is_used": False
            })
            
            if expired_otp:
                flash("OTP has expired. Please request a new one.", "danger")
            else:
                # Add failed login attempt to audit log
                admin_log.insert_one({
                    "email": ADMIN_EMAIL,
                    "action": "login_failed",
                    "timestamp": datetime.datetime.now(),
                    "ip_address": request.remote_addr,
                    "user_agent": request.user_agent.string,
                    "entered_otp": entered_otp
                })
                flash("Invalid OTP. Please try again.", "danger")

    # Get the most recent active OTP for the timer display
    latest_otp = admin_log.find_one(
        {
            "email": ADMIN_EMAIL, 
            "is_used": False,
            "expires_at": {"$gt": datetime.datetime.now()}
        },
        sort=[("created_at", -1)]
    )
    
    # Prevent caching of login page
    response = make_response(render_template("admin/login.html", latest_otp=latest_otp, token=token))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Keep the original login route for backward compatibility, but redirect to the token-based URL
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """Redirect to token-based login URL"""
    # Generate a new token and redirect
    token = generate_secure_token()
    secure_url = url_for("admin.login_with_token", token=token)
    return redirect(secure_url)

@admin_bp.route("/get-otp", methods=["POST"])
def get_otp():
    """Generate and send OTP to admin email"""
    try:
        # Extract token from form data or referer URL to maintain context
        token = request.form.get("token")
        
        # If no token in form, try to extract from referer
        if not token:
            referer = request.referrer
            if referer and '/admin/login/' in referer:
                try:
                    token = referer.split('/admin/login/')[1]
                except:
                    token = None
        
        # Verify token is valid or generate new one
        if token and token in login_tokens:
            # Keep using the valid token
            logger.info(f"Using existing token for OTP request")
        else:
            # Generate new token
            token = generate_secure_token()
            logger.info(f"Generated new token for OTP request")
        
        # Invalidate any existing OTPs
        admin_log.update_many(
            {
                "email": ADMIN_EMAIL,
                "is_used": False
            },
            {"$set": {"is_used": True, "invalidated_at": datetime.datetime.now()}}
        )
        
        # Generate 6-digit OTP
        otp = ''.join(random.choices('0123456789', k=6))
        
        # Set OTP expiration time (5 minutes from now)
        expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
        
        # Store OTP in database
        otp_record = {
            "email": ADMIN_EMAIL,
            "otp": otp,
            "created_at": datetime.datetime.now(),
            "expires_at": expiration_time,
            "is_used": False,
            "request_ip": request.remote_addr,
            "user_agent": request.user_agent.string
        }
        admin_log.insert_one(otp_record)
        
        # Send OTP email
        send_admin_otp(ADMIN_EMAIL, otp)
        
        # Add OTP generation to audit log
        admin_log.insert_one({
            "email": ADMIN_EMAIL,
            "action": "otp_generated",
            "timestamp": datetime.datetime.now(),
            "ip_address": request.remote_addr,
            "user_agent": request.user_agent.string,
            "token": token[:8] + "..." if token else None  # Log partial token for debugging
        })
        
        flash("OTP sent to admin email. Please check your inbox.", "success")
    except Exception as e:
        # Log the error
        admin_log.insert_one({
            "email": ADMIN_EMAIL,
            "action": "otp_generation_failed",
            "error": str(e),
            "timestamp": datetime.datetime.now(),
            "ip_address": request.remote_addr,
            "user_agent": request.user_agent.string
        })
        flash(f"Failed to send OTP: {str(e)}", "danger")
    
    # Redirect back to the token-based login page
    if token:
        return redirect(url_for("admin.login_with_token", token=token))
    else:
        # Fallback to regular login which will generate a new token
        return redirect(url_for("admin.login"))

def send_admin_otp(email, otp):
    """Send admin login OTP email"""
    subject = "Admin Login OTP"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2 style="color: #b03a4c;">Admin Login OTP</h2>
        <p>You requested an OTP to login to the admin panel. Please use the following OTP to complete your login:</p>
        <div style="background-color: #f7f7f7; padding: 15px; font-size: 24px; text-align: center; letter-spacing: 5px; font-weight: bold; margin: 20px 0;">
            {otp}
        </div>
        <p>This OTP will expire in 5 minutes.</p>
        <p>If you did not request this OTP, please ignore this email and contact the system administrator.</p>
        <p>Thank you,<br>Temple Management System</p>
    </div>
    """

    from flask import current_app
    app = current_app

    msg = Message(subject, sender=app.config["MAIL_DEFAULT_SENDER"], recipients=[email])
    msg.html = html_content
    msg.body = f"Your OTP for admin login is: {otp}. It expires in 5 minutes."

    try:
        # Log mail settings before sending
        app.logger.debug(f"Sending admin OTP mail to: {email}")
        mail.send(msg)
        app.logger.info(f"Admin OTP email sent successfully to {email}")
        return True
    except Exception as e:
        app.logger.error(f"Error sending admin OTP email to {email}: {str(e)}")
        raise e

@admin_bp.route("/logout")
def logout():
    """Admin Logout"""
    # Add logout to audit log
    if session.get("admin") == True:
        admin_log.insert_one({
            "email": ADMIN_EMAIL,
            "action": "logout",
            "timestamp": datetime.datetime.now(),
            "ip_address": request.remote_addr,
            "user_agent": request.user_agent.string
        })
    
    # Clear the entire session instead of just removing specific keys
    session.clear()
    flash("You have been logged out.", "info")

    # Prevent caching after logout
    response = make_response(redirect(url_for("general.home")))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@admin_bp.route("/dashboard")
def dashboard():
    """Admin Dashboard"""
    # Redirect to the general admin dashboard
    return redirect(url_for("general_admin.admin_dashboard"))

# Donation goals management routes
@admin_bp.route("/donation-goals")
def donation_goals():
    """Display all donation goals for management"""
    # Redirect to the general admin donation goals management page
    return redirect(url_for("general_admin.manage_donation_goals"))

@admin_bp.route("/donation-goals/add", methods=["POST"])
def add_donation_goal():
    """Add a new donation goal"""
    try:
        # Get form data
        title = request.form.get("title")
        description = request.form.get("description", "")
        target_amount = float(request.form.get("target_amount", 0))
        current_amount = float(request.form.get("current_amount", 0))
        color = request.form.get("color", "primary")
        priority = int(request.form.get("priority", 1))
        active = "active" in request.form
        
        # Validate required fields
        if not title or target_amount <= 0:
            flash("Title and target amount are required", "danger")
            return redirect(url_for("admin.donation_goals"))
        
        # Create new goal document
        goal_data = {
            "title": title,
            "description": description,
            "target_amount": target_amount,
            "current_amount": current_amount,
            "color": color,
            "priority": priority,
            "active": active,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        }
        
        # Insert into database
        donation_goals_collection.insert_one(goal_data)
        
        flash(f"Donation goal '{title}' created successfully", "success")
        return redirect(url_for("admin.donation_goals"))
        
    except Exception as e:
        flash(f"Error creating donation goal: {str(e)}", "danger")
        return redirect(url_for("admin.donation_goals"))

@admin_bp.route("/donation-goals/update", methods=["POST"])
def update_donation_goal():
    """Update an existing donation goal"""
    try:
        # Get form data
        goal_id = request.form.get("goal_id")
        title = request.form.get("title")
        description = request.form.get("description", "")
        target_amount = float(request.form.get("target_amount", 0))
        current_amount = float(request.form.get("current_amount", 0))
        color = request.form.get("color", "primary")
        priority = int(request.form.get("priority", 1))
        active = "active" in request.form
        
        # Validate required fields
        if not goal_id or not title or target_amount <= 0:
            flash("Goal ID, title, and target amount are required", "danger")
            return redirect(url_for("admin.donation_goals"))
        
        # Update goal document
        result = donation_goals_collection.update_one(
            {"_id": ObjectId(goal_id)},
            {"$set": {
                "title": title,
                "description": description,
                "target_amount": target_amount,
                "current_amount": current_amount,
                "color": color,
                "priority": priority,
                "active": active,
                "updated_at": datetime.datetime.now()
            }}
        )
        
        if result.modified_count > 0:
            flash(f"Donation goal '{title}' updated successfully", "success")
        else:
            flash(f"No changes made to donation goal '{title}'", "warning")
            
        return redirect(url_for("admin.donation_goals"))
        
    except Exception as e:
        flash(f"Error updating donation goal: {str(e)}", "danger")
        return redirect(url_for("admin.donation_goals"))

@admin_bp.route("/donation-goals/delete", methods=["POST"])
def delete_donation_goal():
    """Delete a donation goal"""
    try:
        # Get goal ID
        goal_id = request.form.get("goal_id")
        
        if not goal_id:
            flash("Goal ID is required", "danger")
            return redirect(url_for("admin.donation_goals"))
        
        # Get goal info for confirmation message
        goal = donation_goals_collection.find_one({"_id": ObjectId(goal_id)})
        if not goal:
            flash("Donation goal not found", "danger")
            return redirect(url_for("admin.donation_goals"))
        
        # Delete the goal
        donation_goals_collection.delete_one({"_id": ObjectId(goal_id)})
        
        flash(f"Donation goal '{goal.get('title')}' deleted successfully", "success")
        return redirect(url_for("admin.donation_goals"))
        
    except Exception as e:
        flash(f"Error deleting donation goal: {str(e)}", "danger")
        return redirect(url_for("admin.donation_goals"))

@admin_bp.route("/maintenance", methods=["GET", "POST"])
def maintenance_settings():
    """Manage maintenance mode settings"""
    from flask import current_app
    import json
    import os
    import random
    import time
    from database import maintenance_log
    
    # Path to store maintenance status
    try:
        maintenance_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'maintenance_status.json')
        logger.info(f"Using maintenance file path: {maintenance_file}")
    except Exception as e:
        # Fallback to a simple path if there's an issue
        maintenance_file = 'maintenance_status.json'
        logger.error(f"Error with maintenance file path, using fallback: {str(e)}")
    
    # Use Unix timestamp to avoid timezone confusion
    unix_timestamp = int(time.time())
    current_time = datetime.datetime.now()
    
    # Extra debug logging for current state
    logger.info(f"Current maintenance mode state: {current_app.config.get('MAINTENANCE_MODE', False)}")
    logger.info(f"Current session data: {dict(session)}")
    logger.info(f"Current remote IP: {request.remote_addr}")
    
    if request.method == "POST":
        action = request.form.get("action")
        logger.info(f"Maintenance POST request received with action: {action}")
        
        if action == "enable":
            # Check if there's a previous disabled log to calculate uptime
            try:
                last_disabled = maintenance_log.find_one(
                    {"action": "disabled"},
                    sort=[("timestamp_unix", -1)]
                )
                
                uptime_duration = None
                if last_disabled and "timestamp_unix" in last_disabled:
                    # Calculate how long the site was up (in seconds)
                    uptime_duration = unix_timestamp - last_disabled["timestamp_unix"]
                logger.info(f"Last disabled record: {last_disabled}")
                logger.info(f"Calculated uptime duration: {uptime_duration}")
            except Exception as e:
                logger.error(f"Error calculating uptime duration: {str(e)}")
                uptime_duration = None
            
            # Enable maintenance mode
            current_app.config["MAINTENANCE_MODE"] = True
            # Set end time if provided
            end_time = request.form.get("end_time")
            if end_time:
                current_app.config["MAINTENANCE_END_TIME"] = end_time
            
            logger.info(f"Setting maintenance mode to ENABLED with end time: {end_time}")
            
            # Generate a new Unix timestamp for this action
            unix_timestamp = int(time.time())
            
            # Save to file for persistence
            try:
                maintenance_data = {
                    "maintenance_mode": True,
                    "end_time": end_time,
                    "last_updated_unix": unix_timestamp,
                    "action": "enabled"
                }
                
                with open(maintenance_file, 'w') as f:
                    json.dump(maintenance_data, f)
                logger.info(f"Maintenance mode enabled and saved to {maintenance_file} at {unix_timestamp}")
                logger.info(f"Saved maintenance data: {maintenance_data}")
                
                # Verify the file was written correctly by reading it back
                try:
                    with open(maintenance_file, 'r') as f:
                        verify_data = json.load(f)
                    logger.info(f"Verification of saved data: {verify_data}")
                except Exception as e:
                    logger.error(f"Error verifying saved maintenance data: {str(e)}")
            except Exception as e:
                logger.error(f"Error saving maintenance status: {str(e)}")
            
            # Log to maintenance_log collection
            try:
                log_entry = {
                    "action": "enabled",
                    "timestamp_unix": unix_timestamp,
                    "timestamp": datetime.datetime.fromtimestamp(unix_timestamp),
                    "admin_email": ADMIN_EMAIL,
                    "ip_address": request.remote_addr,
                    "user_agent": request.user_agent.string,
                    "end_time": end_time,
                    "uptime_duration": uptime_duration,  # How long the site was up before maintenance
                    "uptime_formatted": format_duration(uptime_duration) if uptime_duration else None
                }
                maintenance_log.insert_one(log_entry)
                logger.info(f"Maintenance mode enabled logged to maintenance_log at {unix_timestamp}")
                logger.info(f"Log entry: {log_entry}")
            except Exception as e:
                logger.error(f"Error logging to maintenance_log: {str(e)}")
            
            flash("Maintenance mode enabled", "success")
            
            # Extra verification after enabling
            logger.info(f"After enabling - Maintenance mode state: {current_app.config.get('MAINTENANCE_MODE', False)}")
        
        elif action == "disable":
            # Check if there's a previous enabled log to calculate downtime
            try:
                last_enabled = maintenance_log.find_one(
                    {"action": "enabled"},
                    sort=[("timestamp_unix", -1)]
                )
                
                downtime_duration = None
                if last_enabled and "timestamp_unix" in last_enabled:
                    # Calculate how long the site was down (in seconds)
                    downtime_duration = unix_timestamp - last_enabled["timestamp_unix"]
                logger.info(f"Last enabled record: {last_enabled}")
                logger.info(f"Calculated downtime duration: {downtime_duration}")
            except Exception as e:
                logger.error(f"Error calculating downtime duration: {str(e)}")
                downtime_duration = None
            
            # Disable maintenance mode
            current_app.config["MAINTENANCE_MODE"] = False
            logger.info("Setting maintenance mode to DISABLED")
            
            # Generate a new Unix timestamp for this action
            unix_timestamp = int(time.time())
            
            # Save to file for persistence
            try:
                maintenance_data = {
                    "maintenance_mode": False,
                    "end_time": "",
                    "last_updated_unix": unix_timestamp,
                    "action": "disabled"
                }
                
                with open(maintenance_file, 'w') as f:
                    json.dump(maintenance_data, f)
                logger.info(f"Maintenance mode disabled and saved to {maintenance_file} at {unix_timestamp}")
                logger.info(f"Saved maintenance data: {maintenance_data}")
                
                # Verify the file was written correctly by reading it back
                try:
                    with open(maintenance_file, 'r') as f:
                        verify_data = json.load(f)
                    logger.info(f"Verification of saved data: {verify_data}")
                except Exception as e:
                    logger.error(f"Error verifying saved maintenance data: {str(e)}")
            except Exception as e:
                logger.error(f"Error saving maintenance status: {str(e)}")
            
            # Log to maintenance_log collection
            try:
                log_entry = {
                    "action": "disabled",
                    "timestamp_unix": unix_timestamp,
                    "timestamp": datetime.datetime.fromtimestamp(unix_timestamp),
                    "admin_email": ADMIN_EMAIL,
                    "ip_address": request.remote_addr,
                    "user_agent": request.user_agent.string,
                    "downtime_duration": downtime_duration,  # How long the site was down
                    "downtime_formatted": format_duration(downtime_duration) if downtime_duration else None
                }
                maintenance_log.insert_one(log_entry)
                logger.info(f"Maintenance mode disabled logged to maintenance_log at {unix_timestamp}")
                logger.info(f"Log entry: {log_entry}")
            except Exception as e:
                logger.error(f"Error logging to maintenance_log: {str(e)}")
            
            flash("Maintenance mode disabled", "success")
            
            # Extra verification after disabling
            logger.info(f"After disabling - Maintenance mode state: {current_app.config.get('MAINTENANCE_MODE', False)}")
    
    # Get current settings
    maintenance_mode = current_app.config.get("MAINTENANCE_MODE", False)
    maintenance_end_time = current_app.config.get("MAINTENANCE_END_TIME", "24 hours")
    bypass_ips = current_app.config.get("MAINTENANCE_BYPASS_IPS", ["127.0.0.1"])
    
    # Read directly from the file for the last updated timestamp
    # Using Unix timestamp to avoid timezone issues
    last_updated_unix = unix_timestamp
    
    try:
        if os.path.exists(maintenance_file):
            with open(maintenance_file, 'r') as f:
                maintenance_data = json.load(f)
                logger.info(f"Read maintenance file during page load: {maintenance_data}")
                
                if "last_updated_unix" in maintenance_data:
                    last_updated_unix = maintenance_data["last_updated_unix"]
                    logger.info(f"Found last_updated_unix in file: {last_updated_unix}")
                else:
                    logger.warning("No last_updated_unix field in maintenance data, using current timestamp")
                
                # Verify that the current_app config matches the file
                if maintenance_mode != maintenance_data.get("maintenance_mode", False):
                    logger.warning(f"Maintenance mode mismatch: app={maintenance_mode}, file={maintenance_data.get('maintenance_mode')}")
        else:
            logger.warning(f"Maintenance file not found at {maintenance_file}, using current timestamp")
    except Exception as e:
        logger.error(f"Error reading maintenance file: {str(e)}")
    
    # Force the page to not be cached
    response = make_response(render_template(
        "admin/maintenance.html",
        maintenance_mode=maintenance_mode,
        maintenance_end_time=maintenance_end_time,
        bypass_ips=bypass_ips,
        last_updated_unix=last_updated_unix
    ))
    
    # Add aggressive cache control headers
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    response.headers["Vary"] = "*"
    response.headers["ETag"] = f"\"{random.randint(0, 999999)}\""
    
    return response

@admin_bp.route("/maintenance-debug")
def maintenance_debug():
    """Debug route to view all maintenance-related database entries"""
    try:
        # Get all maintenance actions from the database
        maintenance_actions = list(admin_log.find(
            {"action": {"$in": ["maintenance_enabled", "maintenance_disabled"]}},
            sort=[("timestamp", -1)]
        ))
        
        # Get current time for comparison
        current_time = datetime.datetime.now()
        ist_current_time = current_time + datetime.timedelta(hours=5, minutes=30)
        
        # Add a debugging message
        logger.info(f"Found {len(maintenance_actions)} maintenance actions")
        for idx, action in enumerate(maintenance_actions):
            logger.info(f"Action {idx+1}: {action.get('action')} at {action.get('timestamp')}")
        
        return render_template(
            "admin/maintenance_debug.html",
            maintenance_actions=maintenance_actions,
            current_time=current_time,
            ist_current_time=ist_current_time
        )
    except Exception as e:
        logger.error(f"Error in maintenance debug: {str(e)}")
        return f"Error retrieving maintenance actions: {str(e)}"

@admin_bp.route("/maintenance-reset", methods=["GET", "POST"])
def maintenance_emergency_reset():
    """Emergency endpoint for resetting maintenance status in case of issues"""
    from flask import current_app
    import json
    import os
    import time
    import random
    
    if request.method == "POST":
        reset_action = request.form.get("reset_action", "disable")
        
        # Get current Unix timestamp
        unix_timestamp = int(time.time())
        
        # Path to maintenance status file
        try:
            maintenance_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'maintenance_status.json')
        except Exception as e:
            maintenance_file = 'maintenance_status.json'
            
        # Create a completely new maintenance status file
        try:
            # First try to delete all database records
            try:
                admin_log.delete_many({"action": {"$in": ["maintenance_enabled", "maintenance_disabled"]}})
            except Exception as e:
                logger.error(f"Failed to reset database records: {str(e)}")
                
            # Update config and write to file
            maintenance_mode = (reset_action == "enable")
            current_app.config["MAINTENANCE_MODE"] = maintenance_mode
            
            # Create maintenance file with fresh data using Unix timestamp
            with open(maintenance_file, 'w') as f:
                json.dump({
                    "maintenance_mode": maintenance_mode,
                    "end_time": "24 hours" if maintenance_mode else "",
                    "last_updated_unix": unix_timestamp,
                    "action": "emergency_reset",
                    "reset_time": unix_timestamp
                }, f)
                
            flash(f"Maintenance mode emergency reset to: {'ENABLED' if maintenance_mode else 'DISABLED'}", "success")
            logger.info(f"Emergency reset performed: maintenance mode set to {maintenance_mode}, timestamp: {unix_timestamp}")
            
            # Log the action in database as well
            try:
                admin_log.insert_one({
                    "email": ADMIN_EMAIL,
                    "action": f"maintenance_emergency_{reset_action}",
                    "timestamp": datetime.datetime.now(),
                    "unix_timestamp": unix_timestamp,
                    "emergency_reset": True,
                    "ip_address": request.remote_addr,
                    "user_agent": request.user_agent.string
                })
            except Exception as e:
                logger.error(f"Failed to log emergency reset action: {str(e)}")
                
        except Exception as e:
            flash(f"Emergency reset failed: {str(e)}", "danger")
            logger.error(f"Emergency reset failed: {str(e)}")
        
        return redirect(url_for("admin.maintenance_settings"))
            
    return render_template(
        "admin/maintenance_reset.html"
    )

@admin_bp.route("/maintenance-logs")
def maintenance_logs():
    """View maintenance mode logs"""
    from database import maintenance_log
    
    try:
        # Get all maintenance logs
        logs = list(maintenance_log.find(
            {},
            sort=[("timestamp_unix", -1)]  # Sort by timestamp descending (newest first)
        ))
        
        # Calculate maintenance statistics
        stats = {
            "total_logs": len(logs),
            "total_enabled": sum(1 for log in logs if log.get("action") == "enabled"),
            "total_disabled": sum(1 for log in logs if log.get("action") == "disabled"),
            "total_auto_enabled": sum(1 for log in logs if log.get("action") == "auto_enabled"),
            "total_auto_disabled": sum(1 for log in logs if log.get("action") == "auto_disabled"),
            "total_downtime": sum(log.get("downtime_duration", 0) or 0 for log in logs if log.get("action") in ["disabled", "auto_disabled"]),
            "total_uptime": sum(log.get("uptime_duration", 0) or 0 for log in logs if log.get("action") in ["enabled", "auto_enabled"]),
            "avg_downtime": 0,
            "avg_uptime": 0
        }
        
        # Calculate totals including automatic actions
        stats["total_all_enabled"] = stats["total_enabled"] + stats["total_auto_enabled"]
        stats["total_all_disabled"] = stats["total_disabled"] + stats["total_auto_disabled"]
        
        # Calculate averages
        total_disable_events = stats["total_disabled"] + stats["total_auto_disabled"]
        if total_disable_events > 0:
            stats["avg_downtime"] = stats["total_downtime"] / total_disable_events
        
        total_enable_events = stats["total_enabled"] + stats["total_auto_enabled"]
        if total_enable_events > 0:
            stats["avg_uptime"] = stats["total_uptime"] / total_enable_events
        
        # Format durations for display
        stats["total_downtime_formatted"] = format_duration(stats["total_downtime"])
        stats["total_uptime_formatted"] = format_duration(stats["total_uptime"])
        stats["avg_downtime_formatted"] = format_duration(stats["avg_downtime"])
        stats["avg_uptime_formatted"] = format_duration(stats["avg_uptime"])
        
        # Count total automatic events
        stats["total_auto_events"] = stats["total_auto_enabled"] + stats["total_auto_disabled"]
        stats["total_manual_events"] = stats["total_enabled"] + stats["total_disabled"]
        
        # Add percentages
        if stats["total_logs"] > 0:
            stats["auto_percentage"] = round((stats["total_auto_events"] / stats["total_logs"]) * 100)
            stats["manual_percentage"] = round((stats["total_manual_events"] / stats["total_logs"]) * 100)
        else:
            stats["auto_percentage"] = 0
            stats["manual_percentage"] = 0
        
        return render_template(
            "admin/maintenance_logs.html",
            logs=logs,
            stats=stats
        )
    except Exception as e:
        logger.error(f"Error retrieving maintenance logs: {str(e)}")
        flash(f"Error retrieving maintenance logs: {str(e)}", "danger")
        return redirect(url_for("admin.maintenance_settings"))
