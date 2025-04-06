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
