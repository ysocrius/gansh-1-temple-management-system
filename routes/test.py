import sys
import os

# Ensure the project root directory is in the Python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # ✅ Add parent directory to sys.path

import database  # ✅ This should now work

print("Successfully imported database.py")
print("Available attributes in database:", dir(database))
