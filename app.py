import sys
import os
import webbrowser
import threading
import time
import logging
from werkzeug.serving import is_running_from_reloader
from datetime import datetime, timezone, timedelta

# Set timezone environment variable for consistent timezone handling
os.environ['TZ'] = 'Asia/Kolkata'  # Set timezone to IST

# Configure logging with more verbose output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('flask_debug.log')
    ]
)
logger = logging.getLogger(__name__)

# Ensure the project root directory is in the Python module search path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)
logger.debug("Project root added to path: %s", project_root)

try:
    logger.debug("Attempting to import Flask app...")
    from app2 import app  # Import Flask app
    logger.debug("Flask app imported successfully")
    logger.debug("Registered blueprints: %s", list(app.blueprints.keys()))
except Exception as e:
    logger.error("Failed to import Flask app: %s", str(e))
    logger.exception("Full traceback:")
    sys.exit(1)

def open_browser():
    """Open a browser after a delay"""
    try:
        time.sleep(1.5)  # Wait for Flask to start
        url = 'http://127.0.0.1:5000'
        logger.debug("Opening browser at: %s", url)
        webbrowser.open(url)
    except Exception as e:
        logger.error("Failed to open browser: %s", str(e))
        logger.exception("Full traceback:")

if __name__ == "__main__":
    try:
        # Log detailed configuration before starting
        logger.debug("Current working directory: %s", os.getcwd())
        logger.debug("Python path: %s", sys.path)
        
        # Log Flask app configuration
        logger.debug("Flask config: %s", {
            "debug": app.debug,
            "testing": app.testing,
            "secret_key_set": bool(app.secret_key),
            "session_interface": str(app.session_interface),
            "template_folder": app.template_folder,
            "static_folder": app.static_folder,
            "registered_blueprints": list(app.blueprints.keys())
        })
        
        # Only open the browser when not running from the reloader process
        if not is_running_from_reloader():
            logger.debug("Starting browser thread")
            threading.Thread(target=open_browser).start()
        
        # Run the Flask app
        logger.info("Starting Flask application")
        app.run(debug=True, host="127.0.0.1", port=5000)
        
    except Exception as e:
        logger.error("Failed to start application: %s", str(e))
        logger.exception("Full traceback:")
        sys.exit(1)