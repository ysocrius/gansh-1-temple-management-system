from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from database import seva_list
from bson.objectid import ObjectId  # Import ObjectId

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



@sevas_bp.route("/admin/delete-seva/<_id>", methods=["POST"])
def delete_seva(_id):
    """Delete a seva from the database"""
    if "admin" not in session:
        return redirect(url_for("admin.login"))  # Ensure only admins can delete

    try:
        object_id = ObjectId(_id)  # Convert _id to ObjectId
        result = seva_list.delete_one({"_id": object_id})  # Delete seva
        
        if result.deleted_count > 0:
            flash("Seva successfully deleted.", "success")
        else:
            flash("Seva not found or already deleted.", "warning")
            
    except Exception as e:
        flash(f"Error deleting seva: {str(e)}", "danger")
        print(f"Error deleting seva: {e}")  # Print error details

    return redirect(url_for("general_admin.manage_sevas"))  # Redirect to the new admin route
