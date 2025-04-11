from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from database import seva_list
from bson.objectid import ObjectId  # Import ObjectId
import random

sevas_bp = Blueprint("sevas", __name__)

@sevas_bp.route("/")
def sevas_list():
    """Public view to display available sevas"""
    # Get filter type from query parameters
    selected_type = request.args.get("type", "all")
    
    if selected_type == "all":
        seva_data = list(seva_list.find())
    else:
        seva_data = list(seva_list.find({"seva_type": selected_type}))
    
    # Convert ObjectId to string for HTML rendering
    for seva in seva_data:
        seva["_id"] = str(seva["_id"])
        
    # Get all seva types for filter dropdown
    seva_types = ["Archanegalu", "Abhishekas", "Alankar", "Pooja/Vratha", "Utsava", "Homa - Kanika"]

    # Render the user-facing template for sevas
    return render_template("user/user_seva.html", sevas=seva_data, seva_types=seva_types, selected_type=selected_type)

@sevas_bp.route("/admin/admin_seva_table")
def seva():
    """Fetch and display all Sevas"""
    seva_data = list(seva_list.find())  # Fetch all sevas from DB
    for seva in seva_data:
        seva["_id"] = str(seva["_id"])  # Convert ObjectId to string for HTML rendering

    return render_template("admin/admin_seva_table.html", sevas=seva_data)  # Correct template path


@sevas_bp.route("/admin/add_seva", methods=["POST"])
def add_seva():
    """Add a new seva to the database"""
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response

    try:
        # Create new seva from form data
        new_seva = {
            "seva_id": request.form["seva_id"],
            "seva_type": request.form["seva_type"],
            "seva_name": request.form["seva_name"],
            "seva_price": request.form["seva_price"],
            "seva_description": request.form["seva_description"],
        }
        
        # Insert into database
        result = seva_list.insert_one(new_seva)
        
        if result.inserted_id:
            flash("New seva added successfully!", "success")
        else:
            flash("Failed to add seva.", "danger")
            
    except Exception as e:
        flash(f"Error adding seva: {str(e)}", "danger")
        print(f"Error adding seva: {e}")

    return redirect(url_for("general_admin.manage_sevas"))



@sevas_bp.route("/admin/delete/<string:seva_id>", methods=['POST'])
def admin_delete_seva(seva_id):
    """Delete a seva (admin only)"""
    # Check if user is logged in as admin
    if 'admin' not in session:
        flash('Admin access required', 'danger')
        return redirect(generate_secure_admin_login_url())  # Ensure only admins can delete
        
    try:
        # Convert ID string to ObjectId
        seva_id_obj = ObjectId(seva_id)
        
        # First, find the seva to get its details for the confirmation message
        seva = seva_list.find_one({'_id': seva_id_obj})
        if not seva:
            flash('Seva not found', 'danger')
            return redirect(url_for('sevas.admin_list_sevas'))
            
        # Delete the seva
        result = seva_list.delete_one({'_id': seva_id_obj})
        
        if result.deleted_count > 0:
            flash(f'Seva "{seva.get("name", "Unknown")}" deleted successfully', 'success')
        else:
            flash('Failed to delete seva', 'danger')
            
    except Exception as e:
        flash(f'Error deleting seva: {str(e)}', 'danger')
        
    return redirect(url_for('sevas.admin_list_sevas'))

# Helper function to generate secure hash for admin login
def generate_secure_admin_login_url():
    """Generate a secure hash and return the URL for admin login with hash"""
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    hash_value = ''.join(random.choices(characters, k=32))
    return url_for("admin.login", hash_value=hash_value)

# Authentication middleware for admin routes
@sevas_bp.before_request
def require_admin():
    """Ensure that only admins can access these routes"""
    # Skip auth check for routes that don't need it
    if not request.path.startswith('/seva/admin'):
        return
        
    # Check if user is logged in as admin
    if 'admin' not in session:
        # Not an admin, redirect to admin login
        flash('Admin access required', 'danger')
        response = redirect(generate_secure_admin_login_url())
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
