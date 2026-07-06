# pyrefly: ignore [missing-import]
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
# pyrefly: ignore [missing-import]
from flask_login import login_user, logout_user, login_required, current_user
from app import database
from app.models import User

auth_bp = Blueprint('auth', __name__)

# Alias for readability
_db = database

ALLOWED_ROLES = ('Hospital Management', 'Police Management')


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def _verify_password(password: str, password_hash: str) -> bool:
    if not password or not password_hash:
        return False
    try:
        stored = password_hash.encode('utf-8') if isinstance(password_hash, str) else password_hash
        return bcrypt.checkpw(password.encode('utf-8'), stored)
    except (ValueError, TypeError):
        return False


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        row = database.fetchone(
            "SELECT * FROM app_user WHERE username = %s AND is_active = TRUE",
            (username,)
        )
        if row and _verify_password(password, row['password_hash']):
            user = User(row['user_id'], row['username'],
                        row['role'], row['staff_id'], row['is_active'])
            login_user(user)
            # update last_login
            database.execute(
                "UPDATE app_user SET last_login = NOW() WHERE user_id = %s",
                (row['user_id'],)
            )
            _db.log_action(row['user_id'], 'LOGIN', 'app_user',
                           row['user_id'], f"User {username} logged in",
                           request.remote_addr)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(request.args.get('next') or url_for('dashboard.home'))
        else:
            flash('Invalid username or password.', 'danger')

    active_tab = request.args.get('tab', 'login')
    if active_tab not in ('login', 'register'):
        active_tab = 'login'
    return render_template('login.html', active_tab=active_tab)


@auth_bp.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    full_name = request.form.get('full_name', '').strip()
    username = request.form.get('reg_username', '').strip()
    password = request.form.get('reg_password', '')
    confirm_password = request.form.get('reg_password_confirm', '')
    role = request.form.get('role', '').strip()

    if not (full_name and username and password and confirm_password and role):
        flash('All fields are required for registration.', 'danger')
        return redirect(url_for('auth.login', tab='register'))

    if len(password) < 6:
        flash('Password must be at least 6 characters.', 'danger')
        return redirect(url_for('auth.login', tab='register'))

    if password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return redirect(url_for('auth.login', tab='register'))

    if role not in ALLOWED_ROLES:
        flash('Invalid role selected.', 'danger')
        return redirect(url_for('auth.login', tab='register'))

    existing = database.fetchone("SELECT user_id FROM app_user WHERE username = %s", (username,))
    if existing:
        flash('Username already exists.', 'danger')
        return redirect(url_for('auth.login', tab='register'))

    hashed = _hash_password(password)

    try:
        staff = database.execute(
            "INSERT INTO staff (full_name, role) VALUES (%s, %s) RETURNING staff_id",
            (full_name, role), returning=True
        )
        staff_id = staff['staff_id']

        new_user = database.execute(
            "INSERT INTO app_user (username, password_hash, role, staff_id, is_active) VALUES (%s, %s, %s, %s, TRUE) RETURNING user_id",
            (username, hashed, role, staff_id), returning=True
        )
        
        _db.log_action(new_user['user_id'], 'INSERT', 'app_user',
                       new_user['user_id'], f"New user {username} registered",
                       request.remote_addr)
        
        flash('Registration successful! Please sign in.', 'success')
    except Exception as e:
        flash('Registration failed due to a server error.', 'danger')
        print(f"Error during registration: {e}")
        return redirect(url_for('auth.login', tab='register'))

    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    _db.log_action(current_user.id, 'LOGOUT', 'app_user',
                   current_user.id, f"User {current_user.username} logged out",
                   request.remote_addr)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))