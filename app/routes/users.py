# pyrefly: ignore [missing-import]
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
# pyrefly: ignore [missing-import]
from flask_login import login_required, current_user
from app.helpers import roles_required
from app import database

users_bp = Blueprint('users', __name__)

UROLES = ['Hospital Management', 'Police Management']


@users_bp.route('/')
@login_required
@roles_required('Hospital Management')
def list_users():
    records = database.fetchall(
        """SELECT u.*, s.full_name AS staff_name FROM app_user u
           LEFT JOIN staff s ON s.staff_id=u.staff_id ORDER BY u.username"""
    )
    return render_template('users/list.html', records=records)


@users_bp.route('/add', methods=['GET','POST'])
@login_required
@roles_required('Hospital Management')
def add_user():
    staff_list = database.fetchall("SELECT staff_id, full_name FROM staff ORDER BY full_name")
    if request.method == 'POST':
        f  = request.form
        pw = bcrypt.hashpw(f['password'].encode(), bcrypt.gensalt()).decode()
        database.execute(
            """INSERT INTO app_user (username, password_hash, role, staff_id)
               VALUES (%s,%s,%s,%s)""",
            (f['username'], pw, f['role'], f.get('staff_id') or None)
        )
        flash(f"User '{f['username']}' created.",'success')
        return redirect(url_for('users.list_users'))
    return render_template('users/form.html', record=None, action='Add',
                           staff_list=staff_list, uroles=UROLES)


@users_bp.route('/<int:uid>/toggle', methods=['POST'])
@login_required
@roles_required('Hospital Management')
def toggle_user(uid):
    user = database.fetchone("SELECT is_active FROM app_user WHERE user_id=%s",(uid,))
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('users.list_users'))
    new_state = not user['is_active']
    database.execute("UPDATE app_user SET is_active=%s WHERE user_id=%s",(new_state, uid))
    flash(f"User {'activated' if new_state else 'deactivated'}.",'info')
    return redirect(url_for('users.list_users'))


@users_bp.route('/<int:uid>/reset-password', methods=['POST'])
@login_required
@roles_required('Hospital Management')
def reset_password(uid):
    new_pw = request.form.get('new_password','')
    if len(new_pw) < 6:
        flash('Password must be at least 6 characters.','danger')
        return redirect(url_for('users.list_users'))
    pw = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
    database.execute("UPDATE app_user SET password_hash=%s WHERE user_id=%s",(pw,uid))
    flash('Password reset.','success')
    return redirect(url_for('users.list_users'))
