"""
Authentication Controller
Handles admin login, logout, and authentication
"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, current_app
from functools import wraps

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/')
def index():
    """Root route - redirect to dashboard or login"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        # Check against environment variables
        if (username == current_app.config['ADMIN_USERNAME'] and 
            password == current_app.config['ADMIN_PASSWORD']):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            if request.is_json:
                return jsonify({'success': True, 'message': 'ログインしました'})
            return redirect(url_for('admin.dashboard'))
        
        error_msg = 'ユーザー名またはパスワードが正しくありません'
        if request.is_json:
            return jsonify({'success': False, 'message': error_msg}), 401
        return render_template('login.html', error=error_msg)
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Logout handler"""
    session.clear()
    return redirect(url_for('auth.login'))
