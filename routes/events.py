from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import events_collection
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import logging
import json
import pymongo

# Set up logging for events
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

events_bp = Blueprint("events", __name__, url_prefix="/admin")

# Helper functions for date handling and event processing
def _get_event_date(event, default_date):
    """Helper method to get event date in datetime format"""
    event_date = event.get("date")
    
    # Handle string dates
    if isinstance(event_date, str):
        try:
            return datetime.strptime(event_date, "%Y-%m-%d")
        except ValueError:
            try:
                # Try alternative format
                return datetime.strptime(event_date, "%d-%m-%Y")
            except ValueError:
                return default_date
    
    # Handle datetime objects
    if isinstance(event_date, datetime):
        return event_date
        
    # Default case
    return default_date

def _process_events_for_template(events, today):
    """Process events for template rendering"""
    processed_events = []
    for event in events:
        try:
            processed_event = event.copy()  # Create a copy to avoid modifying original
            processed_event["_id"] = str(event["_id"])  # Convert ObjectId to string for rendering
            
            # Handle date conversion
            event_date = event.get("date")
            if isinstance(event_date, str):
                try:
                    processed_event["date"] = datetime.strptime(event_date, "%Y-%m-%d")
                except ValueError:
                    try:
                        # Try alternative format
                        processed_event["date"] = datetime.strptime(event_date, "%d-%m-%Y")
                    except ValueError:
                        processed_event["date"] = today
            elif not isinstance(event_date, datetime):
                processed_event["date"] = today
                
            # Ensure all required fields exist
            for field in ["title", "venue", "description"]:
                if field not in processed_event or not processed_event[field]:
                    processed_event[field] = f"No {field} provided"
            
            processed_events.append(processed_event)
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
    
    return processed_events

@events_bp.route("/events")
def events():
    """Fetch and display all events, separating future and past events"""
    try:
        # Log MongoDB connection status
        if events_collection is None:
            logger.error("MongoDB events_collection is None - database connection issue")
            flash("Database connection error. Please contact the administrator.", "danger")
            return render_template('admin/manage_events.html', future_events=[], past_events=[])
        
        logger.info("Fetching events from MongoDB collection")
        
        # Simply get all events
        all_events = list(events_collection.find())
        logger.info(f"Retrieved {len(all_events)} events from database")
        
        # Debug log for each event
        for i, event in enumerate(all_events):
            logger.debug(f"Event {i+1}: ID={event.get('_id')}, Title={event.get('title')}, Date={event.get('date')}")
        
        # Process events
        future_events = []
        past_events = []
        
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for event in all_events:
            # Convert ObjectId to string for template rendering
            event['_id'] = str(event['_id'])
            
            # Ensure we have a proper date object
            event_date = None
            if isinstance(event.get('date'), str):
                try:
                    # Try parsing with different formats
                    for date_format in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y']:
                        try:
                            event_date = datetime.datetime.strptime(event['date'], date_format)
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    logger.error(f"Error parsing date string '{event.get('date')}': {str(e)}")
                    event_date = today  # Default to today if parsing fails
            elif isinstance(event.get('date'), datetime.datetime):
                event_date = event['date']
            else:
                logger.warning(f"Unknown date format for event {event.get('title')}: {type(event.get('date'))}")
                event_date = today  # Default to today if unknown format
            
            # Update the event with proper date
            event['date'] = event_date
            
            # Categorize as future or past
            if event_date >= today:
                future_events.append(event)
            else:
                past_events.append(event)
        
        # Sort events by date
        future_events.sort(key=lambda x: x['date'])
        past_events.sort(key=lambda x: x['date'], reverse=True)
        
        logger.info(f"Processed events: {len(future_events)} future events, {len(past_events)} past events")
        
        return render_template('admin/manage_events.html', future_events=future_events, past_events=past_events)
    
    except Exception as e:
        logger.error(f"Error in events route: {str(e)}")
        flash("An error occurred while retrieving events. Please try again later.", "danger")
        return render_template('admin/manage_events.html', future_events=[], past_events=[])

@events_bp.route("/events-raw-data")
def events_raw_data():
    """Return raw events data as JSON for debugging"""
    try:
        # Get all events without filtering
        all_events = list(events_collection.find())
        
        # Process events for JSON serialization
        processed_events = []
        for event in all_events:
            event_copy = {
                "_id": str(event["_id"]),
                "title": event.get("title", "No title"),
                "date_raw": str(event.get("date", "No date")),
                "date_type": type(event.get("date", None)).__name__,
                "venue": event.get("venue", "No venue"),
                "description": event.get("description", "No description")
            }
            processed_events.append(event_copy)
            
        return jsonify({
            "total_events": len(processed_events),
            "events": processed_events
        })
    except Exception as e:
        logger.error(f"Error fetching raw events data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@events_bp.route("/test-db-connection")
def test_db_connection():
    """Test MongoDB connection and collection access"""
    try:
        from database import client, db
        
        # Test client connection
        client_info = client.server_info()
        
        # Get database stats
        db_stats = db.command("dbstats")
        
        # List collections
        collections = db.list_collection_names()
        
        # Count events
        events_count = events_collection.count_documents({})
        
        # Try to insert and then remove a test document
        test_doc_id = events_collection.insert_one({"test": "connection", "timestamp": datetime.utcnow()}).inserted_id
        events_collection.delete_one({"_id": test_doc_id})
        
        return jsonify({
            "status": "success",
            "mongodb_version": client_info.get("version", "unknown"),
            "database": db.name,
            "collections": collections,
            "events_count": events_count,
            "test_insert_delete": "success"
        })
    except Exception as e:
        logger.error(f"MongoDB connection test failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@events_bp.route("/events-debug")
def events_debug():
    """Debug endpoint to return information about events in JSON format"""
    try:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        thirty_days_ago = today - timedelta(days=30)
        
        # Get a count of all events
        total_count = events_collection.count_documents({})
        future_count = events_collection.count_documents({"date": {"$gte": today}})
        past_count = events_collection.count_documents({
            "date": {
                "$lt": today,
                "$gte": thirty_days_ago
            }
        })
        
        # Get a sample of events (limit to 5 of each)
        future_sample = list(events_collection.find({"date": {"$gte": today}}).sort("date", 1).limit(5))
        past_sample = list(events_collection.find({
            "date": {
                "$lt": today,
                "$gte": thirty_days_ago
            }
        }).sort("date", -1).limit(5))
        
        # Convert ObjectId to string and handle dates for JSON
        for event in future_sample + past_sample:
            event["_id"] = str(event["_id"])
            if isinstance(event.get("date"), datetime):
                event["date"] = event["date"].isoformat()
        
        return jsonify({
            "database_info": {
                "total_events": total_count,
                "future_events_count": future_count,
                "past_events_count": past_count
            },
            "future_events_sample": future_sample,
            "past_events_sample": past_sample,
            "current_date": today.isoformat(),
            "thirty_days_ago": thirty_days_ago.isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in events debug endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@events_bp.route("/event")
def event():
    """Fetch and display only upcoming events"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)  # Midnight UTC

    # Fetch only future events
    events_data = list(events_collection.find({"date": {"$gte": today}}))

    for event in events_data:
        event["_id"] = str(event["_id"])  # Convert ObjectId to string for rendering

    return render_template("events.html", events=events_data)

@events_bp.route("/add_event", methods=["POST"])
def add_event():
    """Handle form submission to add a new event"""
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response

    try:
        # Convert input date (string) to a real datetime object
        event_date = datetime.strptime(request.form["date"], "%Y-%m-%d")

        new_event = {
            "title": request.form["title"],
            "date": event_date,  # Store as datetime instead of string
            "venue": request.form["venue"],
            "description": request.form["description"],
        }
        
        result = events_collection.insert_one(new_event)
        
        if result.inserted_id:
            flash("Event added successfully!", "success")
        else:
            flash("Failed to add event.", "danger")
            
    except ValueError as e:
        logger.error(f"Date format error: {str(e)}")
        flash("Invalid date format. Please use YYYY-MM-DD format.", "danger")
    except Exception as e:
        logger.error(f"Error adding event: {str(e)}")
        flash(f"Error adding event: {str(e)}", "danger")

    # Check if the request came from the general admin page
    referrer = request.referrer
    if referrer and 'general/manage_events' in referrer:
        return redirect(url_for("general_admin.manage_events"))
    else:
        return redirect(url_for("events.events"))

@events_bp.route("/delete-event/<event_id>", methods=["POST"])
def delete_event(event_id):
    """Delete an event manually"""
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response

    try:
        # Delete the event
        result = events_collection.delete_one({"_id": ObjectId(event_id)})
        
        if result.deleted_count > 0:
            flash("Event deleted successfully!", "success")
        else:
            flash("Event not found or already deleted.", "warning")
            
    except Exception as e:
        logger.error(f"Error deleting event: {str(e)}")
        flash(f"Failed to delete Event: {str(e)}", "danger")

    # Check if the request came from the general admin page
    referrer = request.referrer
    if referrer and 'general/manage_events' in referrer:
        return redirect(url_for("general_admin.manage_events"))
    else:
        return redirect(url_for("events.events"))  # Default redirect to events page

@events_bp.route("/cleanup-past-events", methods=["POST"])
def cleanup_past_events():
    """Manually cleanup past events (admin only)"""
    if "admin" not in session:
        flash("Admin access required", "danger")
        response = redirect(url_for("admin.login"))
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
    try:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = events_collection.delete_many({"date": {"$lt": today}})
        
        if result.deleted_count > 0:
            flash(f"Successfully deleted {result.deleted_count} past events.", "success")
        else:
            flash("No past events to delete.", "info")
    except Exception as e:
        logger.error(f"Error cleaning up past events: {str(e)}")
        flash(f"Failed to clean up past events: {str(e)}", "danger")
    
    # Check if the request came from the general admin page
    referrer = request.referrer
    if referrer and 'general/manage_events' in referrer:
        return redirect(url_for("general_admin.manage_events"))
    else:
        return redirect(url_for("events.events"))

@events_bp.route("/add-sample-events")
def add_sample_events():
    """Add sample events for testing"""
    try:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Sample events
        sample_events = [
            {
                "title": "Ganesh Chaturthi",
                "date": today + timedelta(days=5),
                "venue": "Main Temple Hall",
                "description": "Special celebration for Lord Ganesha's birthday"
            },
            {
                "title": "Navratri Celebration",
                "date": today + timedelta(days=15),
                "venue": "Temple Grounds",
                "description": "Nine days of music and dance celebrating the Divine Mother"
            },
            {
                "title": "Monthly Bhajan",
                "date": today - timedelta(days=2),
                "venue": "Community Hall",
                "description": "Monthly devotional singing session"
            },
            {
                "title": "Diwali Festival",
                "date": today + timedelta(days=30),
                "venue": "Temple Complex",
                "description": "Festival of lights with special ceremonies and cultural programs"
            },
            {
                "title": "Yoga Workshop",
                "date": today + timedelta(days=7),
                "venue": "Meditation Hall",
                "description": "Learn traditional yoga practices with experienced teachers"
            }
        ]
        
        # Insert the events
        result = events_collection.insert_many(sample_events)
        
        return jsonify({
            "status": "success",
            "message": f"Added {len(result.inserted_ids)} sample events",
            "event_ids": [str(id) for id in result.inserted_ids]
        })
    except Exception as e:
        logger.error(f"Error adding sample events: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500
