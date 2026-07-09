import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required, ADMIN_ONLY
from app import database

users_bp = Blueprint('users', __name__)


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


@users_bp.route('/')
@login_required
@roles_required(*ADMIN_ONLY)
def list_users():
    users = database.fetchall(
        """SELECT u.*, r.role_name, s.full_name AS staff_name
           FROM app_user u
           JOIN role r ON r.role_id = u.role_id
           LEFT JOIN staff s ON s.staff_id = u.staff_id
           ORDER BY u.username""")
    return render_template('users/list.html', users=users)


@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required(*ADMIN_ONLY)
def add_user():
    roles = database.fetchall("SELECT * FROM role ORDER BY role_name")
    staff = database.fetchall("SELECT staff_id, full_name FROM staff ORDER BY full_name")

    if request.method == 'POST':
        f = request.form
        existing = database.fetchone("SELECT user_id FROM app_user WHERE username=%s", (f['username'],))
        if existing:
            flash('Username already exists.', 'danger')
            return redirect(url_for('users.add_user'))

        hashed = _hash_password(f['password'])
        new = database.execute(
            """INSERT INTO app_user (username, password_hash, role_id, staff_id, is_active)
               VALUES (%s,%s,%s,%s,%s) RETURNING user_id""",
            (f['username'], hashed, f['role_id'], f.get('staff_id') or None,
             'is_active' in f), returning=True
        )
        database.log_action(current_user.id, 'INSERT', 'app_user', new['user_id'], None, 'User created by admin')
        flash('User account created.', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('users/form.html', record=None, action='Add', roles=roles, staff=staff)


@users_bp.route('/<int:uid>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(*ADMIN_ONLY)
def edit_user(uid):
    record = database.fetchone("SELECT * FROM app_user WHERE user_id=%s", (uid,))
    if not record:
        flash('User not found.', 'danger')
        return redirect(url_for('users.list_users'))
    roles = database.fetchall("SELECT * FROM role ORDER BY role_name")
    staff = database.fetchall("SELECT staff_id, full_name FROM staff ORDER BY full_name")

    if request.method == 'POST':
        f = request.form
        if f.get('password'):
            hashed = _hash_password(f['password'])
            database.execute(
                """UPDATE app_user SET username=%s, password_hash=%s, role_id=%s,
                   staff_id=%s, is_active=%s WHERE user_id=%s""",
                (f['username'], hashed, f['role_id'], f.get('staff_id') or None,
                 'is_active' in f, uid)
            )
        else:
            database.execute(
                """UPDATE app_user SET username=%s, role_id=%s, staff_id=%s, is_active=%s
                   WHERE user_id=%s""",
                (f['username'], f['role_id'], f.get('staff_id') or None, 'is_active' in f, uid)
            )
        database.log_action(current_user.id, 'UPDATE', 'app_user', uid, None, 'User updated by admin')
        flash('User updated.', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('users/form.html', record=record, action='Edit', roles=roles, staff=staff)


@users_bp.route('/<int:uid>/delete', methods=['POST'])
@login_required
@roles_required(*ADMIN_ONLY)
def delete_user(uid):
    if uid == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('users.list_users'))
    database.execute("DELETE FROM app_user WHERE user_id=%s", (uid,))
    database.log_action(current_user.id, 'DELETE', 'app_user', uid, None, 'User deleted by admin')
    flash('User deleted.', 'warning')
    return redirect(url_for('users.list_users'))
