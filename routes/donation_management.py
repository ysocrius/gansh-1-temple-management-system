from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import donations_list
from bson.objectid import ObjectId

donation_management_bp = Blueprint("donation_management", __name__, url_prefix="/admin/donations")

@donation_management_bp.route("/", methods=["GET", "POST"])
def manage_donations():
    """Admin page to manage donations"""
    if request.method == "POST":
        donation_id = request.form.get("id")
        donation_name = request.form.get("name")
        donation_description = request.form.get("description")

        if not donation_name or not donation_description:
            flash("Please fill out all fields.", "error")
            return redirect(url_for("donation_management.manage_donations"))

        donation_data = {
            "name": donation_name,
            "id": donation_id,
            "description": donation_description
        }
        result = donations_list.insert_one(donation_data)
        print("Inserted Donation ID:", result.inserted_id)  # Debugging

        flash("Donation added successfully!", "success")
        return redirect(url_for("donation_management.manage_donations"))

    # ✅ Fetch donations and print them for debugging
    donations = list(donations_list.find())
    print("Fetched Donations:", donations)  # Debugging

    return render_template("admin/admin_donation_list.html", donations=donations)

@donation_management_bp.route("/delete/<donation_id>", methods=["POST"])
def delete_donation(donation_id):
    """Delete a donation"""
    try:
        donations_list.delete_one({"_id": ObjectId(donation_id)})
        flash("Donation deleted successfully!", "success")
    except:
        flash("Failed to delete donation. Please try again.", "error")

    return redirect(url_for("donation_management.manage_donations"))  # ✅ Correct redirect
