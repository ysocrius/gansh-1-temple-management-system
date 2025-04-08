from pymongo import MongoClient

# Connect to the MongoDB server
client = MongoClient("mongodb://localhost:27017/")

# Create or access the database
db = client["temple_system"]

# Create or access the collections with proper naming conventions
users_collection = db["users"]  # Collection for storing user data
seva_collection = db["seva_collection"]  # Collection for storing seva bookings

donations_collection = db["donations"]  # Collection for storing donations
donations_list = db["donations_list"]
events_collection = db["events"]  # Collection for storing events
admin_log = db["admin_log"]  # Collection for storing admin login OTPs and audit logs

# Ensure collections are accessible for imports
__all__ = ["users_collection", "seva_collection", "seva_list", "donations_collection", "events_collection", "donations_list", "admin_log"]

# Sample structure for each collection:
# Users Collection Example:
# {
#     "username": "user1",
#     "password": "hashed_password",
#     "email": "user1@example.com",
#     "role": "user"  # Can be 'user' or 'admin'
# }

# Seva Bookings Collection Example:
# {
#     "name": "John Doe",
#     "email": "johndoe@example.com",
#     "phone": "1234567890",
#     "seva_type": "Abhishekam",
#     "date": "2025-02-20"
# }

# Donations Collection Example:
# {
#     "name": "John Doe",
#     "amount": 500,
#     "donation_date": "2025-02-19",
#     "message": "Supporting temple maintenance"
# }

# Events Collection Example:
# {
#     "title": "Annual Festival",
#     "date": "2025-02-20",
#     "venue": "Temple Grounds",
#     "description": "A celebration with cultural programs and special pooja"
# }
