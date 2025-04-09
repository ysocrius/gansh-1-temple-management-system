from flask import Blueprint, render_template, request, redirect, url_for, session, make_response, flash
from database import user_collection, seva_collection, donations_collection, admin_log
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

# Configure logger
logger = logging.getLogger(__name__)

# Add reference to donation_goals_collection
from database import db
donation_goals_collection = db.donation_goals

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Admin email configuration - Update this with your actual admin email
ADMIN_EMAIL = "yeshwanthcr108@gmail.com"

# Authentication middleware for admin routes
@admin_bp.before_request
def require_admin():
    # Skip auth check for login page and get-otp endpoints
    if request.endpoint in ["admin.login", "admin.get_otp"]:
        return

    # Check if user is logged in and is an admin
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
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

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """Admin Login Page with OTP Verification"""
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
    response = make_response(render_template("admin/login.html", latest_otp=latest_otp))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@admin_bp.route("/get-otp", methods=["POST"])
def get_otp():
    """Generate and send OTP to admin email"""
    try:
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
            "user_agent": request.user_agent.string
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
    
    # Path to store maintenance status
    try:
        maintenance_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'maintenance_status.json')
    except Exception as e:
        # Fallback to a simple path if there's an issue
        maintenance_file = 'maintenance_status.json'
        logger.error(f"Error with maintenance file path, using fallback: {str(e)}")
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "enable":
            # Delete all previous maintenance records to ensure timestamp freshness
            try:
                delete_result = admin_log.delete_many({"action": {"$in": ["maintenance_enabled", "maintenance_disabled"]}})
                logger.info(f"Deleted {delete_result.deleted_count} old maintenance records")
            except Exception as e:
                logger.error(f"Error deleting old maintenance records: {str(e)}")
                
            # Enable maintenance mode
            current_app.config["MAINTENANCE_MODE"] = True
            # Set end time if provided
            end_time = request.form.get("end_time")
            if end_time:
                current_app.config["MAINTENANCE_END_TIME"] = end_time
            
            # Save to file for persistence
            try:
                with open(maintenance_file, 'w') as f:
                    json.dump({
                        "maintenance_mode": True,
                        "end_time": end_time
                    }, f)
                logger.info(f"Maintenance mode enabled and saved to {maintenance_file}")
            except Exception as e:
                logger.error(f"Error saving maintenance status: {str(e)}")
            
            # Log the action with IST timezone (UTC+5:30)
            try:
                # Add 5.5 hours to timestamp for IST
                current_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
                # Generate a unique action ID to ensure we can find this specific action
                action_id = f"maintenance_{int(time.time())}"
                admin_log.insert_one({
                    "email": ADMIN_EMAIL,
                    "action": "maintenance_enabled",
                    "action_id": action_id,
                    "timestamp": current_time,
                    "ip_address": request.remote_addr,
                    "user_agent": request.user_agent.string,
                    "end_time": end_time
                })
                logger.info(f"Logged maintenance enable action with ID: {action_id} at time: {current_time}")
            except Exception as e:
                logger.error(f"Error logging maintenance action: {str(e)}")
            
            flash("Maintenance mode enabled", "success")
        
        elif action == "disable":
            # Delete all previous maintenance records to ensure timestamp freshness
            try:
                delete_result = admin_log.delete_many({"action": {"$in": ["maintenance_enabled", "maintenance_disabled"]}})
                logger.info(f"Deleted {delete_result.deleted_count} old maintenance records")
            except Exception as e:
                logger.error(f"Error deleting old maintenance records: {str(e)}")
                
            # Disable maintenance mode
            current_app.config["MAINTENANCE_MODE"] = False
            
            # Save to file for persistence
            try:
                with open(maintenance_file, 'w') as f:
                    json.dump({
                        "maintenance_mode": False,
                        "end_time": ""
                    }, f)
                logger.info(f"Maintenance mode disabled and saved to {maintenance_file}")
            except Exception as e:
                logger.error(f"Error saving maintenance status: {str(e)}")
            
            # Log the action with IST timezone (UTC+5:30)
            try:
                # Add 5.5 hours to timestamp for IST
                current_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
                # Generate a unique action ID to ensure we can find this specific action
                action_id = f"maintenance_{int(time.time())}"
                admin_log.insert_one({
                    "email": ADMIN_EMAIL,
                    "action": "maintenance_disabled",
                    "action_id": action_id,
                    "timestamp": current_time,
                    "ip_address": request.remote_addr,
                    "user_agent": request.user_agent.string
                })
                logger.info(f"Logged maintenance disable action with ID: {action_id} at time: {current_time}")
            except Exception as e:
                logger.error(f"Error logging maintenance action: {str(e)}")
            
            flash("Maintenance mode disabled", "success")
    
    # Get current settings
    maintenance_mode = current_app.config.get("MAINTENANCE_MODE", False)
    maintenance_end_time = current_app.config.get("MAINTENANCE_END_TIME", "24 hours")
    bypass_ips = current_app.config.get("MAINTENANCE_BYPASS_IPS", ["127.0.0.1"])
    
    # Get the last maintenance action for the timestamp - using current time as fallback
    last_updated = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
    try:
        # Use more specific query and force a refresh by setting a high limit
        last_action = admin_log.find_one(
            {"action": {"$in": ["maintenance_enabled", "maintenance_disabled"]}},
            sort=[("timestamp", -1)],
            limit=1
        )
        if last_action and "timestamp" in last_action:
            last_updated = last_action["timestamp"]
            logger.info(f"Found last maintenance action: {last_action.get('action')} at {last_updated}")
        else:
            logger.warning("No maintenance action found in database, using current time")
    except Exception as e:
        logger.error(f"Error retrieving last maintenance action: {str(e)}")
    
    # Force the page to not be cached
    response = make_response(render_template(
        "admin/maintenance.html",
        maintenance_mode=maintenance_mode,
        maintenance_end_time=maintenance_end_time,
        bypass_ips=bypass_ips,
        last_updated=last_updated
    ))
    
    # Add cache control headers to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
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
