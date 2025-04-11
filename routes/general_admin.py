from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from database import seva_collection, events_collection, donations_collection, donations_list, seva_list, user_collection, bill_collection
from datetime import datetime
from bson.objectid import ObjectId
from bson import ObjectId
import time
import json
import logging
from utils.db import get_db
from bson.json_util import dumps
from utils.decorators import admin_required

# Import donation goals collection
try:
    from database import donation_goals_collection
except ImportError:
    from database import db
    donation_goals_collection = db.donation_goals

general_admin_bp = Blueprint("general_admin", __name__, url_prefix="/admin/general")  # ✅ Fixed URL prefix

@general_admin_bp.after_request
def add_cache_headers(response):
    """Add cache control headers to all general admin routes"""
    # Add cache control headers to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@general_admin_bp.route("/dashboard")
def admin_dashboard():
    """Admin Dashboard with statistics and recent activities"""

    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))  # Ensure only admins access this page
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response

    # Get statistics from collections
    stats = {
        "events": {
            "total": events_collection.count_documents({}),
            "upcoming": events_collection.count_documents({"date": {"$gte": datetime.now()}}),
            "recent_events": list(events_collection.find().sort("date", -1).limit(5))
        },
        "sevas": {
            "total_types": seva_list.count_documents({}),
            "total_bookings": seva_collection.count_documents({}),
            "recent_bookings": list(seva_collection.find().sort("_id", -1).limit(5))
        },
        "donations": {
            "total_types": donations_list.count_documents({}),
            "total_donations": donations_collection.count_documents({}),
            "recent_donations": list(donations_collection.find().sort("_id", -1).limit(5)),
            "total_amount": sum(float(donation.get("amount", 0)) for donation in donations_collection.find())
        },
        "users": {
            "total": user_collection.count_documents({}),
            "verified": user_collection.count_documents({"verified": True})
        },
        "bills": {
            "total": bill_collection.count_documents({}),
            "recent_bills": list(bill_collection.find().sort("_id", -1).limit(5)),
            "total_amount": sum(bill.get("total_amount", 0) for bill in bill_collection.find())
        },
        "donation_goals": {
            "total": donation_goals_collection.count_documents({}),
            "active": donation_goals_collection.count_documents({"active": True}),
            "recent_goals": list(donation_goals_collection.find().sort("created_at", -1).limit(3)),
            "total_target": sum(goal.get("target_amount", 0) for goal in donation_goals_collection.find()),
            "total_raised": sum(goal.get("current_amount", 0) for goal in donation_goals_collection.find()),
        }
    }
    
    # Process dates in event objects
    for event in stats["events"]["recent_events"]:
        event["_id"] = str(event["_id"])
        if isinstance(event.get("date"), datetime):
            event["date_formatted"] = event["date"].strftime("%d-%m-%Y")
    
    # Process IDs in seva bookings
    for booking in stats["sevas"]["recent_bookings"]:
        booking["_id"] = str(booking["_id"])
    
    # Process IDs in donations
    for donation in stats["donations"]["recent_donations"]:
        donation["_id"] = str(donation["_id"])
    
    # Process IDs in bills
    for bill in stats["bills"]["recent_bills"]:
        bill["_id"] = str(bill["_id"])
    
    # Process donation goals
    for goal in stats["donation_goals"]["recent_goals"]:
        goal["_id"] = str(goal["_id"])
        # Ensure consistent field names
        if "current" in goal and "current_amount" not in goal:
            goal["current_amount"] = goal.get("current", 0)
        if "goal" in goal and "target_amount" not in goal:
            goal["target_amount"] = goal.get("goal", 0)
        # Calculate progress percentage
        goal["progress_percentage"] = int((goal.get("current_amount", 0) / goal.get("target_amount", 1)) * 100) if goal.get("target_amount", 0) > 0 else 0
        
    # Current timestamp for display
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    return render_template("admin/admin_dashboard.html", stats=stats, current_time=current_time)

@general_admin_bp.route("/manage_sevas")
def manage_sevas():
    """Admin view to manage sevas"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
        
    sevas = list(seva_list.find())  
    return render_template("admin/admin_seva_table.html", sevas=sevas)

@general_admin_bp.route("/manage_events")
def manage_events():
    """Admin view to manage events"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
        
    try:
        # Fetch events from MongoDB
        all_events = list(events_collection.find())
        
        # Process events
        future_events = []
        past_events = []
        
        # Get current date (midnight)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for event in all_events:
            # Convert ObjectId to string for rendering
            event["_id"] = str(event["_id"])
            
            # Ensure we have a proper date object
            event_date = None
            if isinstance(event.get("date"), str):
                try:
                    # Try parsing with different formats
                    for date_format in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]:
                        try:
                            event_date = datetime.strptime(event["date"], date_format)
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    # Default to today if parsing fails
                    event_date = today
            elif isinstance(event.get("date"), datetime):
                event_date = event["date"]
            else:
                # Default to today for unknown date formats
                event_date = today
            
            # Update the event with proper date
            event["date"] = event_date
            
            # Categorize as future or past
            if event_date >= today:
                future_events.append(event)
            else:
                past_events.append(event)
        
        # Sort events by date
        future_events.sort(key=lambda x: x["date"])
        past_events.sort(key=lambda x: x["date"], reverse=True)
        
        return render_template("admin/manage_events.html", future_events=future_events, past_events=past_events)
    
    except Exception as e:
        flash(f"Error loading events: {str(e)}", "danger")
        return render_template("admin/manage_events.html", future_events=[], past_events=[])

@general_admin_bp.route("/manage_donations")
def manage_donations():
    """Admin view to manage donations"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
        
    try:
        # Get all donations
        all_donations = list(donations_collection.find().sort("date", -1))
        
        # Convert ObjectId to string for template
        for donation in all_donations:
            if "_id" in donation:
                donation["_id"] = str(donation["_id"])
            if "user_id" in donation and isinstance(donation["user_id"], ObjectId):
                donation["user_id"] = str(donation["user_id"])
        
        # Get all donation types
        all_donation_types = list(donations_list.find())
        
        # Convert ObjectId to string for template
        for donation_type in all_donation_types:
            if "_id" in donation_type:
                donation_type["_id"] = str(donation_type["_id"])
        
        return render_template(
            "admin/admin_donation_list.html", 
            donations=all_donations,
            donation_types=all_donation_types
        )
    except Exception as e:
        flash(f"Error loading donations: {str(e)}", "danger")
        return redirect(url_for("general_admin.admin_dashboard"))

@general_admin_bp.route("/manage_donation_goals")
def manage_donation_goals():
    """Admin view to manage donation goals"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
    try:
        # Fetch all donation goals with sorting
        donation_goals = list(donation_goals_collection.find().sort("priority", 1))
        
        # Convert ObjectId to string for template
        for goal in donation_goals:
            goal["_id"] = str(goal["_id"])
        
        return render_template("admin/manage_donation_goals.html", donation_goals=donation_goals)
    except Exception as e:
        flash(f"Error loading donation goals: {str(e)}", "danger")
        return redirect(url_for("general_admin.admin_dashboard"))

@general_admin_bp.route("/donation_goals/add", methods=["POST"])
def add_donation_goal():
    """Add a new donation goal"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
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
            return redirect(url_for("general_admin.manage_donation_goals"))
        
        # Create new goal document
        goal_data = {
            "title": title,
            "description": description,
            "target_amount": target_amount,
            "current_amount": current_amount,
            "color": color,
            "priority": priority,
            "active": active,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Insert into database
        donation_goals_collection.insert_one(goal_data)
        
        flash(f"Donation goal '{title}' created successfully", "success")
        return redirect(url_for("general_admin.manage_donation_goals"))
        
    except Exception as e:
        flash(f"Error creating donation goal: {str(e)}", "danger")
        return redirect(url_for("general_admin.manage_donation_goals"))

@general_admin_bp.route("/donation_goals/update", methods=["POST"])
def update_donation_goal():
    """Update an existing donation goal"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
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
            return redirect(url_for("general_admin.manage_donation_goals"))
        
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
                "updated_at": datetime.now()
            }}
        )
        
        if result.modified_count > 0:
            flash(f"Donation goal '{title}' updated successfully", "success")
        else:
            flash(f"No changes made to donation goal '{title}'", "warning")
            
        return redirect(url_for("general_admin.manage_donation_goals"))
        
    except Exception as e:
        flash(f"Error updating donation goal: {str(e)}", "danger")
        return redirect(url_for("general_admin.manage_donation_goals"))

@general_admin_bp.route("/donation_goals/delete", methods=["POST"])
def delete_donation_goal():
    """Delete a donation goal"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
    try:
        # Get form data
        goal_id = request.form.get("goal_id")
        
        if not goal_id:
            flash("Goal ID is required", "danger")
            return redirect(url_for("general_admin.manage_donation_goals"))
        
        # Get goal info for confirmation message
        goal = donation_goals_collection.find_one({"_id": ObjectId(goal_id)})
        if not goal:
            flash("Donation goal not found", "danger")
            return redirect(url_for("general_admin.manage_donation_goals"))
        
        # Delete the goal
        donation_goals_collection.delete_one({"_id": ObjectId(goal_id)})
        
        flash(f"Donation goal '{goal.get('title')}' deleted successfully", "success")
        return redirect(url_for("general_admin.manage_donation_goals"))
        
    except Exception as e:
        flash(f"Error deleting donation goal: {str(e)}", "danger")
        return redirect(url_for("general_admin.manage_donation_goals"))

@general_admin_bp.route("/manage_testimonials")
def manage_testimonials():
    """Admin view to manage testimonials"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
    db = get_db()
    testimonials = list(db.testimonials.find().sort('date_submitted', -1))
    for testimonial in testimonials:
        testimonial['_id'] = str(testimonial['_id'])
        testimonial['user_id'] = str(testimonial['user_id'])
    
    # Create a proper response object to set headers on
    rendered_template = render_template('admin/manage_testimonials.html', testimonials=testimonials)
    response = make_response(rendered_template)
    
    # Add cache control headers to prevent browser caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

@general_admin_bp.route("/approve_testimonial/<testimonial_id>", methods=["POST"])
def approve_testimonial(testimonial_id):
    """Approve a testimonial"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
    db = get_db()
    db.testimonials.update_one(
        {'_id': ObjectId(testimonial_id)},
        {'$set': {'status': 'approved'}}
    )
    flash('Testimonial approved successfully', 'success')
    return redirect(url_for('general_admin.manage_testimonials'))

@general_admin_bp.route("/reject_testimonial/<testimonial_id>", methods=["POST"])
def reject_testimonial(testimonial_id):
    """Reject a testimonial"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
    db = get_db()
    db.testimonials.update_one(
        {'_id': ObjectId(testimonial_id)},
        {'$set': {'status': 'rejected'}}
    )
    flash('Testimonial rejected successfully', 'success')
    return redirect(url_for('general_admin.manage_testimonials'))

@general_admin_bp.route("/add_donation_type", methods=["POST"])
def add_donation_type():
    """Add a new donation type"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
    try:
        # Get form data
        donation_id = request.form.get("id")
        name = request.form.get("name")
        description = request.form.get("description")
        min_amount = int(request.form.get("min_amount", 100))
        
        # Validate required fields
        if not donation_id or not name or not description:
            flash("All fields are required", "danger")
            return redirect(url_for("general_admin.manage_donations"))
        
        # Check if donation type already exists
        existing = donations_list.find_one({"id": donation_id})
        if existing:
            flash(f"Donation type with ID '{donation_id}' already exists", "danger")
            return redirect(url_for("general_admin.manage_donations"))
        
        # Create new donation type
        donation_type = {
            "id": donation_id,
            "name": name,
            "description": description,
            "min_amount": min_amount,
            "created_at": datetime.now()
        }
        
        # Insert into database
        result = donations_list.insert_one(donation_type)
        
        if result.inserted_id:
            flash(f"Donation type '{name}' added successfully", "success")
        else:
            flash("Failed to add donation type", "danger")
            
    except Exception as e:
        flash(f"Error adding donation type: {str(e)}", "danger")
    
    return redirect(url_for("general_admin.manage_donations"))

@general_admin_bp.route("/delete_donation/<donation_id>", methods=["POST"])
def delete_donation(donation_id):
    """Delete a donation"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
    try:
        # Delete the donation
        result = donations_collection.delete_one({"_id": ObjectId(donation_id)})
        
        if result.deleted_count > 0:
            flash("Donation deleted successfully", "success")
        else:
            flash("Donation not found or already deleted", "warning")
            
    except Exception as e:
        flash(f"Error deleting donation: {str(e)}", "danger")
    
    return redirect(url_for("general_admin.manage_donations"))

@general_admin_bp.route("/delete_donation_type/<type_id>", methods=["POST"])
def delete_donation_type(type_id):
    """Delete a donation type"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
    try:
        # Get the donation type to display in the confirmation message
        donation_type = donations_list.find_one({"_id": ObjectId(type_id)})
        
        if not donation_type:
            flash("Donation type not found", "warning")
            return redirect(url_for("general_admin.manage_donations"))
        
        # Delete the donation type
        result = donations_list.delete_one({"_id": ObjectId(type_id)})
        
        if result.deleted_count > 0:
            flash(f"Donation type '{donation_type.get('name')}' deleted successfully", "success")
        else:
            flash("Donation type not found or already deleted", "warning")
            
    except Exception as e:
        flash(f"Error deleting donation type: {str(e)}", "danger")
    
    return redirect(url_for("general_admin.manage_donations"))

@general_admin_bp.route("/manage_users")
def manage_users():
    """Admin view to manage users"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        return redirect(url_for("admin.login"))
    
    try:
        # Get filter and search parameters
        filter_option = request.args.get('filter', 'all')
        search_query = request.args.get('search', '')
        
        # Build the query based on filters and search
        query = {}
        
        # Apply filters
        if filter_option == 'verified':
            query['verified'] = True
        elif filter_option == 'unverified':
            query['verified'] = False
        
        # Apply search if provided
        if search_query:
            query['$or'] = [
                {'name': {'$regex': search_query, '$options': 'i'}},
                {'email': {'$regex': search_query, '$options': 'i'}}
            ]
        
        # Get users with pagination
        users = list(user_collection.find(query).sort('created_at', -1))
        
        # Process user data for template
        for user in users:
            user['_id'] = str(user['_id'])
        
        # Count statistics
        total_users = user_collection.count_documents({})
        verified_users = user_collection.count_documents({'verified': True})
        
        return render_template(
            "admin/manage_users.html",
            users=users,
            total_users=total_users,
            verified_users=verified_users
        )
        
    except Exception as e:
        flash(f"Error loading users: {str(e)}", "danger")
        return redirect(url_for("general_admin.admin_dashboard"))

@general_admin_bp.route("/get_user/<user_id>")
def get_user(user_id):
    """Get detailed information about a user"""
    # Check for admin authentication
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Convert string ID to ObjectId
        user_id_obj = ObjectId(user_id)
        
        # Find the user
        user = user_collection.find_one({"_id": user_id_obj})
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get user activity counts
        seva_count = seva_collection.count_documents({"user_id": str(user_id)})
        donation_count = donations_collection.count_documents({"user_id": str(user_id)})
        
        # Prepare user data
        user_data = {
            "_id": str(user["_id"]),
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "phone": user.get("phone", ""),
            "address": user.get("address", ""),
            "verified": user.get("verified", False),
            "created_at": user.get("created_at").strftime("%d-%m-%Y %H:%M") if user.get("created_at") else "Unknown",
            "seva_count": seva_count,
            "donation_count": donation_count
        }
        
        return jsonify(user_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@general_admin_bp.route("/verify_user/<user_id>", methods=["POST"])
def verify_user(user_id):
    """Verify a user's account"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        return redirect(url_for("admin.login"))
    
    try:
        # Convert string ID to ObjectId
        user_id_obj = ObjectId(user_id)
        
        # Update the user's verification status
        result = user_collection.update_one(
            {"_id": user_id_obj},
            {"$set": {"verified": True}}
        )
        
        if result.modified_count:
            flash("User has been verified successfully.", "success")
        else:
            flash("Failed to verify user. User may not exist.", "danger")
            
        return redirect(url_for("general_admin.manage_users"))
        
    except Exception as e:
        flash(f"Error verifying user: {str(e)}", "danger")
        return redirect(url_for("general_admin.manage_users"))

@general_admin_bp.route("/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    """Delete a user's account"""
    # Check for admin authentication
    if "admin" not in session:
        flash("Admin access required", "danger")
        return redirect(url_for("admin.login"))
    
    try:
        # Convert string ID to ObjectId
        user_id_obj = ObjectId(user_id)
        
        # Get user information for logging
        user = user_collection.find_one({"_id": user_id_obj})
        
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("general_admin.manage_users"))
        
        # Delete the user
        result = user_collection.delete_one({"_id": user_id_obj})
        
        if result.deleted_count:
            # Log deletion
            logging.info(f"Admin deleted user: {user.get('email')} (ID: {user_id})")
            flash("User has been deleted successfully.", "success")
        else:
            flash("Failed to delete user.", "danger")
            
        return redirect(url_for("general_admin.manage_users"))
        
    except Exception as e:
        flash(f"Error deleting user: {str(e)}", "danger")
        return redirect(url_for("general_admin.manage_users"))

# ✅ Route for adding new sevas

