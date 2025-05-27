# instance/config.py
import os

# Define the base directory of the instance folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Configuration for file uploads
# It's generally recommended to store uploads outside the main application directory 
# if possible, or ensure the 'instance' folder is not directly web-accessible if it's inside.
# For this project, we'll use a subdirectory within the instance folder.
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Flask-SQLAlchemy (example, assuming it might be here, otherwise in main config)
# SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
#     'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
# SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key for session management etc.
# SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

# Ensure the upload folder exists
# os.makedirs(UPLOAD_FOLDER, exist_ok=True) # This will be done by a bash command later

# You can add other instance-specific configurations here.
# For example, API keys, specific database URIs for production, etc.

print(f"Instance config loaded. UPLOAD_FOLDER set to: {UPLOAD_FOLDER}")
