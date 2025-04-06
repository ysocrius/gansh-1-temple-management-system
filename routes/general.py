from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify, current_app, request, make_response
from database import seva_collection, donations_collection, seva_list, donations_list, events_collection  # ✅ Added history_collection import
from bson.objectid import ObjectId
from datetime import datetime
import logging
import functools
from cachelib import SimpleCache
from utils.db import get_db

# Set up logging for the general routes
logger = logging.getLogger(__name__)

# Create a simple memory cache with a 5-minute timeout
cache = SimpleCache(default_timeout=300)

general_bp = Blueprint('general', __name__)

def cached(timeout=300):
    """Decorator for caching view functions"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f.__name__ + str(args) + str(kwargs)
            rv = cache.get(cache_key)
            if rv is None:
                rv = f(*args, **kwargs)
                cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

@general_bp.route("/")
def home():
    """Home page route"""
    try:
        # Get recent donations (limit to 4 most recent)
        recent_donations_cursor = donations_collection.find().sort("_id", -1).limit(4)
        recent_donations = []
        
        # Process donations in Python
        for donation in recent_donations_cursor:
            donation["_id"] = str(donation["_id"])
            recent_donations.append(donation)
        
        # Sample temple announcements (in a real app, this would come from a database)
        announcements = [
            {
                "id": 1,
                "title": "Temple Renovation Project",
                "excerpt": "We are pleased to announce the commencement of our temple renovation project, which will enhance the spiritual experience for all devotees.",
                "date": "April 10, 2023",
                "image": "announcement1.jpg"
            },
            {
                "id": 2,
                "title": "New Chief Priest Appointment",
                "excerpt": "We warmly welcome our new chief priest, Shri Venkata Sharma, who brings 20 years of experience and deep spiritual knowledge to our temple.",
                "date": "March 28, 2023",
                "image": "announcement2.jpg"
            },
            {
                "id": 3,
                "title": "Community Service Initiative",
                "excerpt": "Our temple is launching a new community service program aimed at providing food and educational support to underprivileged children in our area.",
                "date": "March 15, 2023",
                "image": "announcement3.jpg"
            }
        ]
        
        # Get recent approved testimonials
        db = get_db()
        testimonials_cursor = db.testimonials.find({"status": "approved"}).sort("date_submitted", -1).limit(3)
        testimonials = []
        
        for testimonial in testimonials_cursor:
            testimonials.append({
                "id": str(testimonial["_id"]),
                "name": testimonial["user_name"],
                "title": f"Rating: {testimonial['rating']}/5",
                "content": testimonial["message"],
                "date": testimonial["date_submitted"].strftime("%B %d, %Y")
            })
        
        # Disable caching of this page by setting a response header in the rendered template
        response = make_response(render_template('user/index.html', 
                              upcoming_events=[],  # Passing empty list to maintain template compatibility
                              recent_donations=recent_donations,
                              announcements=announcements,
                              testimonials=testimonials))
        
        # Add cache control headers to prevent browser caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    except Exception as e:
        logger.error(f"Error loading homepage: {str(e)}")
        return render_template('user/index.html', 
                              upcoming_events=[],
                              recent_donations=[],
                              announcements=[],
                              testimonials=[])

@general_bp.route("/gallery")
def gallery():
    return render_template("user/gallery.html")

@general_bp.route("/pooja-timings")
def pooja_timings():
    return render_template("user/pooja_timings.html")

@general_bp.route("/events")
def events():
    """Public events page showing upcoming and recent past events"""
    try:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get upcoming events
        upcoming_events = list(events_collection.find({"date": {"$gte": today}}).sort("date", 1))
        
        # Get recent past events (last 7 days)
        seven_days_ago = datetime(today.year, today.month, today.day)
        seven_days_ago = seven_days_ago.replace(day=max(1, today.day - 7))
        past_events = list(events_collection.find({
            "date": {
                "$lt": today,
                "$gte": seven_days_ago
            }
        }).sort("date", -1))
        
        # Process event dates
        for event in upcoming_events + past_events:
            event["_id"] = str(event["_id"])
            if isinstance(event["date"], str):
                event["date"] = datetime.strptime(event["date"], "%Y-%m-%d")
                
        logger.debug(f"Displaying {len(upcoming_events)} upcoming and {len(past_events)} past events")
        return render_template('user/events.html', 
                              upcoming_events=upcoming_events,
                              past_events=past_events)
    except Exception as e:
        logger.error(f"Error loading events page: {str(e)}")
        flash("An error occurred while loading events. Please try again later.", "error")
        return render_template('user/events.html', upcoming_events=[], past_events=[])

@general_bp.route("/donations")
def general_donations():
    """Public view to display available donations"""
    # Fetch all available donation types
    donation_types = list(donations_list.find())
    
    # Fetch recent donations (limit to 10 most recent)
    recent_donations_cursor = donations_collection.find().sort("date", -1).limit(10)
    recent_donations = []
    
    # Process each donation and convert dates
    for donation in recent_donations_cursor:
        try:
            # Convert string date to datetime if it's a string
            if isinstance(donation.get('date'), str):
                donation['date'] = datetime.fromisoformat(donation['date'])
            elif not isinstance(donation.get('date'), datetime):
                # If date is missing or invalid, use current time
                donation['date'] = datetime.now()
        except (ValueError, TypeError):
            # Handle invalid date format
            donation['date'] = datetime.now()
        
        recent_donations.append(donation)
    
    # Calculate statistics
    statistics = {}
    
    # Calculate total sevas
    statistics['total_sevas'] = seva_collection.count_documents({})
    
    # Calculate total donations
    statistics['total_donations'] = donations_collection.count_documents({})
    
    # Calculate total donation amount
    donations_cursor = donations_collection.find()
    total_amount = sum(float(donation.get('amount', 0)) for donation in donations_cursor)
    statistics['total_amount'] = total_amount
    formatted_total = "{:,.2f}".format(total_amount)
    
    return render_template("user/donations.html", 
                         donation_types=donation_types, 
                         recent_donations=recent_donations,
                         total_amount=formatted_total,
                         statistics=statistics,
                         is_debug=True)

@general_bp.route("/e-hundi")
def e_hundi():
    return render_template("user/e_hundi.html")

@general_bp.route("/general-sevas")
def get_general_sevas():  # Function name updated to avoid conflicts
    """Public view to display available sevas"""
    # Get filter type from query parameters
    selected_type = request.args.get("type", "all")
    
    if selected_type == "all":
        sevas_data = list(seva_list.find())
    else:
        sevas_data = list(seva_list.find({"seva_type": selected_type}))

    for seva in sevas_data:
        seva["_id"] = str(seva["_id"])  # Convert ObjectId to string

    # Use the dedicated template for general-sevas with client-side filtering
    return render_template("user/general_sevas.html", sevas=sevas_data, selected_type=selected_type)

@general_bp.route("/logout")
def logout():
    """General Logout"""
    # Clear the entire session instead of just removing user_id
    session.clear()
    flash("You have been logged out.", "info")
    
    # Redirect to home page with cache control headers
    response = redirect(url_for("general.home"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

@general_bp.route("/temple-history")
def temple_history():
    """Temple history page"""
    return render_template("user/temple_history.html")

@general_bp.route("/contact")
def contact():
    """Contact page with temple information and FAQs"""
    return render_template("user/contact.html")

@general_bp.route("/privacy-policy")
def privacy_policy():
    """Privacy Policy page"""
    return render_template("user/privacy_policy.html")

@general_bp.route("/terms-of-service")
def terms_of_service():
    """Terms of Service page"""
    return render_template("user/terms_of_service.html")

@general_bp.route("/check-session")
def check_session():
    """Debug route to check session contents"""
    is_authenticated = 'user_id' in session
    
    return jsonify({
        'session': dict(session),
        'authenticated': is_authenticated
    })
