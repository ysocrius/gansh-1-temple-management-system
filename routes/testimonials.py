from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from bson import ObjectId
from datetime import datetime
from utils.db import get_db
from utils.decorators import login_required, admin_required

testimonials = Blueprint('testimonials', __name__, url_prefix='/testimonials')

@testimonials.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    if request.method == 'POST':
        user_id = session.get('user', {}).get('id')
        user_name = session.get('user', {}).get('name')
        
        testimonial_data = {
            'user_id': ObjectId(user_id),
            'user_name': user_name,
            'message': request.form.get('message'),
            'rating': int(request.form.get('rating')),
            'date_submitted': datetime.utcnow(),
            'status': 'pending'  # pending, approved, rejected
        }
        
        db = get_db()
        db.testimonials.insert_one(testimonial_data)
        flash('Thank you for your testimonial! It will be reviewed shortly.', 'success')
        return redirect(url_for('user.dashboard'))
        
    return render_template('user/submit_testimonial.html')

@testimonials.route('/admin/manage', methods=['GET'])
@admin_required
def manage():
    """Redirect to the new admin route"""
    return redirect(url_for('general_admin.manage_testimonials'))

@testimonials.route('/admin/approve/<testimonial_id>', methods=['POST'])
@admin_required
def approve(testimonial_id):
    """Redirect to the new admin approve route"""
    return redirect(url_for('general_admin.approve_testimonial', testimonial_id=testimonial_id))

@testimonials.route('/admin/reject/<testimonial_id>', methods=['POST'])
@admin_required
def reject(testimonial_id):
    """Redirect to the new admin reject route"""
    return redirect(url_for('general_admin.reject_testimonial', testimonial_id=testimonial_id)) 