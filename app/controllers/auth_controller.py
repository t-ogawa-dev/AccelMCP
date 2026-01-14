"""
Authentication Controller
Handles admin login, logout, and authentication with brute-force protection
"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, current_app
from functools import wraps
from datetime import datetime, timedelta, UTC
from concurrent.futures import ThreadPoolExecutor
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# Thread pool for async log writing
_executor = ThreadPoolExecutor(max_workers=2)


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


def _get_client_ip():
    """Get client IP address from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '0.0.0.0'


def _get_lock_settings():
    """Get login lock settings from AdminSettings"""
    from app.models.models import AdminSettings
    
    max_attempts = AdminSettings.query.filter_by(setting_key='login_max_attempts').first()
    lock_duration = AdminSettings.query.filter_by(setting_key='login_lock_duration_minutes').first()
    
    return {
        'max_attempts': int(max_attempts.setting_value) if max_attempts else 5,
        'lock_duration_minutes': int(lock_duration.setting_value) if lock_duration else 30
    }


def _check_lock_status(ip_address):
    """Check if IP is currently locked (without incrementing counter)"""
    from app.models.models import LoginLockStatus
    
    settings = _get_lock_settings()
    lock_status = LoginLockStatus.query.filter_by(ip_address=ip_address).first()
    
    if lock_status and lock_status.is_locked():
        remaining_minutes = int((lock_status.locked_until - datetime.now(UTC).replace(tzinfo=None)).total_seconds() / 60)
        return True, f'アカウントがロックされています。残り約{remaining_minutes}分後に解除されます。'
    
    return False, None


def _check_and_update_lock_status(ip_address, is_success=False):
    """Check if IP is locked and update lock status"""
    from app.models.models import db, LoginLockStatus
    
    settings = _get_lock_settings()
    lock_status = LoginLockStatus.query.filter_by(ip_address=ip_address).first()
    
    if lock_status:
        # Check if currently locked
        if lock_status.is_locked():
            remaining_minutes = int((lock_status.locked_until - datetime.now(UTC).replace(tzinfo=None)).total_seconds() / 60)
            return True, f'アカウントがロックされています。残り約{remaining_minutes}分後に解除されます。'
        
        # If lock period has expired, reset the counter
        if lock_status.locked_until and lock_status.locked_until < datetime.now(UTC).replace(tzinfo=None):
            lock_status.failed_attempts = 0
            lock_status.locked_until = None
        
        if is_success:
            # Reset on successful login
            lock_status.failed_attempts = 0
            lock_status.locked_until = None
        else:
            # Increment failed attempts
            lock_status.failed_attempts += 1
            lock_status.last_attempt_at = datetime.now(UTC).replace(tzinfo=None)
            
            # Lock if threshold exceeded
            if lock_status.failed_attempts >= settings['max_attempts']:
                lock_status.locked_until = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=settings['lock_duration_minutes'])
                db.session.commit()
                return True, f'ログイン試行回数が上限に達しました。{settings["lock_duration_minutes"]}分間ロックされます。'
        
        lock_status.updated_at = datetime.now(UTC).replace(tzinfo=None)
        db.session.commit()
    else:
        # Create new lock status record
        if not is_success:
            lock_status = LoginLockStatus(
                ip_address=ip_address,
                failed_attempts=1,
                last_attempt_at=datetime.now(UTC).replace(tzinfo=None)
            )
            db.session.add(lock_status)
            db.session.commit()
    
    return False, None


def _log_login_attempt(username, ip_address, user_agent, is_success, failure_reason=None, session_id=None):
    """Log login attempt asynchronously (or synchronously in test mode)"""
    import os
    
    def _write_log():
        try:
            from app.models.models import db, AdminLoginLog
            from flask import current_app
            
            # In test mode, use current app context (synchronous)
            if os.environ.get('TESTING') or current_app.config.get('TESTING'):
                log_entry = AdminLoginLog(
                    created_at=datetime.now(UTC).replace(tzinfo=None),
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    is_success=is_success,
                    failure_reason=failure_reason,
                    session_id=session_id
                )
                db.session.add(log_entry)
                db.session.commit()
                logger.debug(f"Login attempt logged: {username} from {ip_address} - {'Success' if is_success else 'Failure'}")
            else:
                # Production mode: create new app context (asynchronous)
                from app import create_app
                app = create_app()
                with app.app_context():
                    log_entry = AdminLoginLog(
                        created_at=datetime.now(UTC).replace(tzinfo=None),
                        username=username,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        is_success=is_success,
                        failure_reason=failure_reason,
                        session_id=session_id
                    )
                    db.session.add(log_entry)
                    db.session.commit()
                    logger.debug(f"Login attempt logged: {username} from {ip_address} - {'Success' if is_success else 'Failure'}")
        except Exception as e:
            logger.error(f"Failed to log login attempt: {e}")
    
    # In test mode, execute synchronously
    if os.environ.get('TESTING'):
        _write_log()
    else:
        _executor.submit(_write_log)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler with brute-force protection"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '')
        password = data.get('password', '')
        
        ip_address = _get_client_ip()
        user_agent = request.headers.get('User-Agent', '')[:500]
        
        # Check if IP is locked (without incrementing counter)
        is_locked, lock_message = _check_lock_status(ip_address)
        if is_locked:
            _log_login_attempt(username, ip_address, user_agent, False, 'account_locked')
            if request.is_json:
                return jsonify({'success': False, 'message': lock_message}), 429
            return render_template('login.html', error=lock_message)
        
        # Validate credentials
        if (username == current_app.config['ADMIN_USERNAME'] and 
            password == current_app.config['ADMIN_PASSWORD']):
            # Success - clear lock status
            _check_and_update_lock_status(ip_address, is_success=True)
            
            session.clear()
            session.permanent = True
            session['admin_logged_in'] = True
            session['admin_username'] = username
            
            # Log successful login
            _log_login_attempt(username, ip_address, user_agent, True, session_id=session.sid if hasattr(session, 'sid') else None)
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'ログインしました'})
            return redirect(url_for('admin.dashboard'))
        
        # Login failed - determine reason
        if username != current_app.config['ADMIN_USERNAME']:
            failure_reason = 'invalid_username'
        else:
            failure_reason = 'invalid_password'
        
        # Update lock status (increment failed attempts)
        _check_and_update_lock_status(ip_address, is_success=False)
        
        # Log failed login
        _log_login_attempt(username, ip_address, user_agent, False, failure_reason)
        
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
