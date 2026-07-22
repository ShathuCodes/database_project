from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def roles_required(*roles):
    """Decorator: redirect to dashboard with flash error if user is not authorized."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash(f"Access Denied: Your role ({current_user.role}) is not authorized to access this feature.", "danger")
                return redirect(url_for('dashboard.home'))
            return f(*args, **kwargs)
        return wrapped
    return decorator


# Standardized Role Groups across the App
ALL_ROLES  = ('Administrator', 'Senior JMO', 'JMO', 'Lab Technician', 'Clerk')
CLINICAL   = ('Administrator', 'Senior JMO', 'JMO')
LAB_ROLES  = ('Administrator', 'Senior JMO', 'JMO', 'Lab Technician')
ADMIN_ONLY = ('Administrator',)
