from functools import wraps
from flask import abort
from flask_login import current_user


def roles_required(*roles):
    """Decorator: abort 403 if logged-in user's role is not in roles."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


# Role groups used across the app
ALL_ROLES     = ('Administrator', 'Senior JMO', 'JMO', 'Lab Technician', 'Clerk')
CLINICAL      = ('Administrator', 'Senior JMO', 'JMO')
LAB_ROLES     = ('Administrator', 'Senior JMO', 'JMO', 'Lab Technician')
ADMIN_ONLY    = ('Administrator',)
