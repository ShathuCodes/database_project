# pyrefly: ignore [missing-import]
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
# pyrefly: ignore [missing-import]
from flask_login import login_user, logout_user, login_required, current_user
from app import database
from app.models import User
from app.helpers import ALL_ROLES

auth_bp = Blueprint('auth', __name__)

# Designations available for self-registration (maps 1:1 onto a role of the same name,
# except Clerk/Lab Technician staff use the matching STAFF.designation)
REGISTER_ROLES = ['JMO', 'Senior JMO', 'Lab Technician', 'Clerk']
DESIGNATION_FOR_ROLE = {
    'Senior JMO':    'Senior JMO',
    'JMO':           'JMO',
    'Lab Technician':'Tech Officer',
    'Clerk':         'Clerk',
}


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


# ── Landing page ──────────────────────────────────────────────────────────────
@auth_bp.route('/')
def index():
    """Root route: authenticated → dashboard, otherwise → landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    return redirect(url_for('auth.landing'))


@auth_bp.route('/landing')
def landing():
    """Public marketing / landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    return render_template('landing.html')


# ── Sign In ────────────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Sign-in page (GET) and authentication handler (POST)."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('signin.html')

        row = database.fetchone(
            """SELECT u.user_id, u.username, u.password_hash, u.staff_id,
                      u.is_active, r.role_name AS role
               FROM app_user u
               JOIN role r ON r.role_id = u.role_id
               WHERE u.username = %s""",
            (username,)
        )

        if not row:
            flash('Invalid username or password.', 'danger')
            return render_template('signin.html')

        if not row.get('is_active'):
            flash('Your account has been deactivated. Please contact the administrator.', 'warning')
            return render_template('signin.html')

        if not _verify_password(password, row['password_hash']):
            flash('Invalid username or password.', 'danger')
            return render_template('signin.html')

        # Successful login
        user = User(row['user_id'], row['username'],
                    row['role'], row['staff_id'], row['is_active'])
        login_user(user)

        try:
            database.execute(
                "UPDATE app_user SET last_login = NOW() WHERE user_id = %s",
                (row['user_id'],)
            )
            database.log_action(
                row['user_id'], 'UPDATE', 'app_user',
                row['user_id'], None, f"User {username} logged in",
                request.remote_addr
            )
        except Exception as e:
            # Non-fatal: login succeeded, logging failed
            print(f"Warning: could not update last_login or audit log: {e}")

        flash(f'Welcome back, {username}!', 'success')
        next_url = request.args.get('next') or url_for('dashboard.home')
        return redirect(next_url)

    # GET
    return render_template('signin.html')


# ── Sign Up (GET) ──────────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET'])
def register_page():
    """Sign-up page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    return render_template('signup.html', register_roles=REGISTER_ROLES)


# ── Sign Up (POST) ─────────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    """Process the registration form."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    full_name        = request.form.get('full_name', '').strip()
    username         = request.form.get('reg_username', '').strip()
    password         = request.form.get('reg_password', '')
    confirm_password = request.form.get('reg_password_confirm', '')
    role             = request.form.get('role', '').strip()

    # ── Validate ──────────────────────────────────────────────
    def _fail(msg):
        flash(msg, 'danger')
        return render_template('signup.html', register_roles=REGISTER_ROLES)

    if not all([full_name, username, password, confirm_password, role]):
        return _fail('All fields are required for registration.')

    if len(username) < 3:
        return _fail('Username must be at least 3 characters.')

    if len(password) < 6:
        return _fail('Password must be at least 6 characters.')

    if password != confirm_password:
        return _fail('Passwords do not match.')

    if role not in REGISTER_ROLES:
        return _fail('Invalid role selected.')

    existing = database.fetchone(
        "SELECT user_id FROM app_user WHERE username = %s", (username,)
    )
    if existing:
        return _fail('That username is already taken. Please choose another.')

    role_row = database.fetchone(
        "SELECT role_id FROM role WHERE role_name = %s", (role,)
    )
    if not role_row:
        return _fail('The selected role is not configured. Contact the administrator.')

    # ── Create staff + user ───────────────────────────────────
    hashed      = _hash_password(password)
    designation = DESIGNATION_FOR_ROLE.get(role, 'Clerk')

    try:
        staff = database.execute(
            "INSERT INTO staff (full_name, designation) VALUES (%s, %s) RETURNING staff_id",
            (full_name, designation), returning=True
        )
        staff_id = staff['staff_id']

        new_user = database.execute(
            """INSERT INTO app_user (username, password_hash, role_id, staff_id, is_active)
               VALUES (%s, %s, %s, %s, TRUE) RETURNING user_id""",
            (username, hashed, role_row['role_id'], staff_id), returning=True
        )

        database.log_action(
            new_user['user_id'], 'INSERT', 'app_user',
            new_user['user_id'], None, f"New user {username} registered",
            request.remote_addr
        )

        flash('Account created successfully! Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    except Exception as e:
        print(f"Error during registration: {e}")
        return _fail('Registration failed due to a server error. Please try again.')


# ── Logout ─────────────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    try:
        database.log_action(
            current_user.id, 'UPDATE', 'app_user',
            current_user.id, None, f"User {current_user.username} logged out",
            request.remote_addr
        )
    except Exception as e:
        print(f"Warning: logout audit log failed: {e}")

    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
