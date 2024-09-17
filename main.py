import os
from dotenv import load_dotenv
from flask import Flask
from app.routes.guest_routes import guest_bp
from app.routes.admin_routes import admin_bp
from flask_migrate import Migrate, upgrade
from config import db

# Import your models after db is defined
from app.models import Guest, Room, Booking, Table, TableReservation, Payment, RoomCategory

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Set a secret key for sessions (loaded from environment variables)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Load the SQLAlchemy database URL from environment variables
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')

# Initialize the database with the app
db.init_app(app)

# Initialize Flask-Migrate for handling migrations
migrate = Migrate(app, db)

# Register Blueprints for guest and admin routes
app.register_blueprint(guest_bp, url_prefix='/')
app.register_blueprint(admin_bp, url_prefix='/admin')

def run_migrations():
    """
    Run migrations automatically when the app starts.
    """
    with app.app_context():
        try:
            upgrade()  # Automatically run flask db upgrade
            print("Database migration applied successfully.")
        except Exception as e:
            print(f"Error running migrations: {e}")

if __name__ == "__main__":
    # Run migrations and start the Flask application
    run_migrations()
    app.run(debug=True)
