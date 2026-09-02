from flask import Blueprint, render_template, redirect, url_for, session
from services.attendance_service import get_dashboard_stats

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('auth.login'))
        
    stats = get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)
