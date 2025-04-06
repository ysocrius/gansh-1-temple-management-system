from pymongo import MongoClient
from bson.binary import Binary
import os


# ✅ Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://24mscs25:yHDoxmEYf96ZEvrx@cluster0.ox5xbz4.mongodb.net/temple_system?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(mongo_uri)
db = client["temple_system"]

# ✅ Define collections
seva_collection = db["seva_bookings"]
seva_list = db["seva_list"]
events_collection = db["events_collection"]
user_collection = db["user_collection"]
donations_collection = db["donations_collection"]
donations_list = db["donations_list"]
order_details = db["order_details"]
bill_collection = db["bill_collection"]
donation_goals_collection = db["donation_goals"]
testimonial_collection = db["testimonials"]


def get_database():
    """Return the database instance"""
    return db

def initialize_db():
    print("Database initialized successfully!")

def get_user_by_email(email):
    """Fetch user details from MongoDB using their email."""
    user = user_collection.find_one({"email": email})

    if user:
        password_hash = user.get("password", "")  # Get password hash (default to empty string if missing)
        verified = user.get("verified", False)  # ✅ Fetch 'verified' status (default to False)

        # Convert Binary data to string if stored as Binary
        if isinstance(password_hash, Binary):
            password_hash = password_hash.decode("utf-8")  

        return {
            "id": str(user["_id"]),  # Convert ObjectId to string
            "email": user["email"],
            "password": password_hash,  # Ensure password is a string
            "verified": verified  # ✅ Include 'verified' field
        }
    return None  # Return None if user not found

