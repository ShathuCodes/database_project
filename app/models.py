# pyrefly: ignore [missing-import]
from flask_login import UserMixin
import app.database as database


class User(UserMixin):
    def __init__(self, user_id, username, role, staff_id, is_active):
        self.id       = user_id
        self.username = username
        self.role     = role          # role_name string, e.g. 'Administrator'
        self.staff_id = staff_id
        self._active  = is_active

    @property
    def is_active(self):
        return self._active

    def has_role(self, *roles):
        return self.role in roles


def load_user(user_id):
    row = database.fetchone(
        """SELECT u.user_id, u.username, u.staff_id, u.is_active, r.role_name AS role
           FROM app_user u
           JOIN role r ON r.role_id = u.role_id
           WHERE u.user_id = %s""",
        (user_id,)
    )
    if row:
        return User(row['user_id'], row['username'],
                     row['role'], row['staff_id'], row['is_active'])
    return None
