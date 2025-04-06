from flask import Blueprint, render_template, request, redirect, url_for, session, make_response, flash
from database import user_collection, seva_collection, donations_collection
from bson.objectid import ObjectId
import datetime
import json
import os
import sys

# Add reference to donation_goals_collection
from database import db
donation_goals_collection = db.donation_goals

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ADMIN_CREDENTIALS = {"username": "admin", "password": "admin"}

# Authentication middleware for admin routes
@admin_bp.before_request
def require_admin():
    # Skip auth check for login page
    if request.endpoint == "admin.login":
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
    """Admin Login Page"""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
            session["admin"] = True
            if "user" not in session:
                session["user"] = {}
            session["user"]["is_admin"] = True
            return redirect(url_for("general_admin.admin_dashboard"))
        else:
            return render_template("admin/login.html", message="Invalid credentials!")

    # Prevent caching of login page
    response = make_response(render_template("admin/login.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@admin_bp.route("/logout")
def logout():
    """Admin Logout"""
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
