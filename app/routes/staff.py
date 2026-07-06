# pyrefly: ignore [missing-import]
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
# pyrefly: ignore [missing-import]
from flask_login import login_required, current_user
from app.helpers import roles_required
from app import database

staff_bp = Blueprint('staff', __name__)

ROLES = ['Hospital Management', 'Police Management']

# ── STAFF ──────────────────────────────────────────────────

@staff_bp.route('/')
@login_required
@roles_required('Hospital Management')
def list_staff():
    search = request.args.get('search','').strip()
    role   = request.args.get('role','')
    sql    = "SELECT * FROM staff WHERE 1=1"
    params = []
    if search:
        sql += " AND (full_name ILIKE %s OR email ILIKE %s)"
        params.extend([f'%{search}%']*2)
    if role:
        sql += " AND role=%s"
        params.append(role)
    sql += " ORDER BY full_name"
    records = database.fetchall(sql, params)
    return render_template('staff/list.html', records=records,
                           roles=ROLES, search=search, role=role)


@staff_bp.route('/add', methods=['GET','POST'])
@login_required
@roles_required('Hospital Management')
def add_staff():
    if request.method == 'POST':
        f = request.form
        database.execute(
            """INSERT INTO staff (full_name, role, specialization, contact, email)
               VALUES (%s,%s,%s,%s,%s)""",
            (f['full_name'], f['role'], f.get('specialization'),
             f.get('contact'), f.get('email') or None)
        )
        flash('Staff member added.','success')
        return redirect(url_for('staff.list_staff'))
    return render_template('staff/form.html', record=None, action='Add', roles=ROLES)


@staff_bp.route('/<int:sid>/edit', methods=['GET','POST'])
@login_required
@roles_required('Hospital Management')
def edit_staff(sid):
    record = database.fetchone("SELECT * FROM staff WHERE staff_id=%s",(sid,))
    if not record:
        flash('Staff member not found.', 'danger')
        return redirect(url_for('staff.list_staff'))
    if request.method == 'POST':
        f = request.form
        database.execute(
            """UPDATE staff SET full_name=%s, role=%s, specialization=%s,
               contact=%s, email=%s WHERE staff_id=%s""",
            (f['full_name'], f['role'], f.get('specialization'),
             f.get('contact'), f.get('email') or None, sid)
        )
        flash('Staff updated.','success')
        return redirect(url_for('staff.list_staff'))
    return render_template('staff/form.html', record=record, action='Edit', roles=ROLES)


@staff_bp.route('/<int:sid>/delete', methods=['POST'])
@login_required
@roles_required('Hospital Management')
def delete_staff(sid):
    database.execute("DELETE FROM staff WHERE staff_id=%s",(sid,))
    flash('Staff deleted.','warning')
    return redirect(url_for('staff.list_staff'))