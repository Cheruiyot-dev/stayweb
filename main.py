from flask import Flask
from app.routes.guest_routes import guest_bp
from app.routes.admin_routes import admin_bp
from flask_migrate import Migrate
from config import db
import os

# Import your models after db is defined
from app.models import Guest, Room, Booking, Table, TableReservation, Payment, RoomCategory

# Initialize the app
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'

# Load config from a config file or environment variables
# app.config.from_object('config.Config')

# app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:1092@localhost/havenstaydb'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://havenstaydb_user:VCTJku33iQdUah7E5uLNLCGgXonRj1aB@dpg-crkculbv2p9s73b5ehsg-a.oregon-postgres.render.com/havenstaydb'


db.init_app(app)

# Register Blueprints for guest and admin routes
app.register_blueprint(guest_bp, url_prefix='/')
app.register_blueprint(admin_bp, url_prefix='/admin')

migrate = Migrate(app, db)

def create_tables():
    """
    Function to create tables if they don't exist
    """
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")

if __name__ == "__main__":
    # Ensure tables are created before running the app
    with app.app_context():
        create_tables()
    app.run(debug=True)