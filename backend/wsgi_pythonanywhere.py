"""
WSGI configuration for PythonAnywhere deployment

Copy this file content to your WSGI configuration file on PythonAnywhere.
The WSGI file is located in the Web tab of your PythonAnywhere dashboard.

IMPORTANT: Replace 'YOUR_USERNAME' with your actual PythonAnywhere username!
"""

import sys
import os

# Add your project directory to the sys.path
# Replace 'YOUR_USERNAME' with your PythonAnywhere username
project_home = '/home/YOUR_USERNAME/gym-management-system'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
load_dotenv(env_path)

# Set Flask environment to production
os.environ['FLASK_ENV'] = 'production'

# Import Flask application
from app import create_app

# Create the application instance
application = create_app('production')

# For debugging purposes (remove in production)
# Uncomment the lines below if you need to debug
# import logging
# logging.basicConfig(level=logging.DEBUG)
# application.logger.setLevel(logging.DEBUG)
