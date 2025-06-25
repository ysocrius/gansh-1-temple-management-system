from pymongo import MongoClient
import pprint

# Connect to MongoDB
#client = MongoClient('mongodb+srv://24mscs25:yHDoxmEYf96ZEvrx@cluster0.ox5xbz4.mongodb.net/temple_system')
db = client['temple_system']

# List all collections
print("Collections:", db.list_collection_names())

# Check if admin_log exists
if 'admin_log' in db.list_collection_names():
    print("\nAdmin Log Collection exists!")
    
    # Count documents
    count = db.admin_log.count_documents({})
    print(f"Total documents: {count}")
    
    # Show OTP records
    otp_records = db.admin_log.find({"otp": {"$exists": True}})
    print(f"\nOTP Records ({db.admin_log.count_documents({'otp': {'$exists': True}})} total):")
    for doc in otp_records:
        print(f"- OTP: {doc.get('otp')} | Created: {doc.get('created_at')} | Used: {doc.get('is_used')}")
    
    # Show action logs
    action_logs = db.admin_log.find({"action": {"$exists": True}})
    print(f"\nAction Logs ({db.admin_log.count_documents({'action': {'$exists': True}})} total):")
    for doc in action_logs:
        print(f"- Action: {doc.get('action')} | Time: {doc.get('timestamp')}")
else:
    print("Admin Log Collection does not exist!") 
