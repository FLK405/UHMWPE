from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes import main_bp, api_bp, auth_bp  # Import the blueprints
    app.register_blueprint(main_bp) # Register the main blueprint
    app.register_blueprint(api_bp)  # Register the API blueprint
    app.register_blueprint(auth_bp) # Register the Auth blueprint

    # Import models here if they are needed for app initialization (e.g. for db.create_all())
    # from app import models

    return app
