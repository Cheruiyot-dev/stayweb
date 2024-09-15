from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

# Define admin routes


@admin_bp.route('/admin/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Add more admin routes as needed
