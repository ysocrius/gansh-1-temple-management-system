import os
from dotenv import load_dotenv

load_dotenv()  # ✅ Load environment variables from .env

class Config:
    # ✅ Flask Secret Key
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

    # ✅ Email Configuration - Hardcoded for Gmail
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "yeshwanthcr108@gmail.com"
    MAIL_PASSWORD = "vbqcptpnblofsvuj"
    MAIL_DEFAULT_SENDER = "yeshwanthcr108@gmail.com"

    # ✅ MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/temple_system")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "temple_system")
    
    # ✅ Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # ✅ Maintenance Mode Configuration
    MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "False").lower() == "true"
    # Use environment variable or default to localhost, make sure admin IPs can always access
    MAINTENANCE_BYPASS_IPS = os.getenv("MAINTENANCE_BYPASS_IPS", "127.0.0.1").split(",")
    # Allow admin paths to always be accessible
    MAINTENANCE_BYPASS_PATHS = [
        '/static/',  # Allow static resources
        '/favicon.ico',
        '/admin/',  # Allow all admin routes
        '/maintenance-preview',  # Allow maintenance preview
        '/toggle-maintenance',  # Allow maintenance toggle endpoint
        '/check-auth',  # Allow authentication check
        '/test-maintenance'  # Allow maintenance test route
    ]
    MAINTENANCE_END_TIME = os.getenv("MAINTENANCE_END_TIME", "24 hours")  # Display text for maintenance end time