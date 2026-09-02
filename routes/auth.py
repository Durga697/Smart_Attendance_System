from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def login():
    if 'admin_logged_in' in session:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
        admin = cursor.fetchone()
        connection.close()
        
        if admin:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))
