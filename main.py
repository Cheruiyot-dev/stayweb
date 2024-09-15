from flask import Flask
from app.routes.guest_routes import guest_bp
from app.routes.admin_routes import admin_bp
import os

app = Flask(__name__, template_folder='app/templates',static_folder='app/static')

# Register the Blueprint for guest routes
app.register_blueprint(guest_bp, url_prefix='/')
app.register_blueprint(admin_bp, url_prefix='/admin')

print("Absolute path of template folder:", os.path.abspath(app.template_folder))

if __name__ == "__main__":
    app.run(debug=True)

