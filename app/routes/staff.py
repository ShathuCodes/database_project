from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required, ADMIN_ONLY, ALL_ROLES
from app import database

staff_bp = Blueprint('staff', __name__)

DESIGNATIONS = ['Senior JMO', 'JMO', 'PG Trainee', 'Tech Officer', 'Clerk']


@staff_bp.route('/')
@login_required
@roles_required(*ALL_ROLES)
def list_staff():
    search = request.args.get('search', '').strip()
    sql = "SELECT * FROM staff WHERE 1=1"
    params = []
    if search:
        sql += " AND (full_name ILIKE %s OR slmc_regno ILIKE %s)"
        params.extend([f'%{search}%'] * 2)
    sql += " ORDER BY full_name"
    staff_list = database.fetchall(sql, params)
    return render_template('staff/list.html', staff_list=staff_list, search=search)


@staff_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required(*ADMIN_ONLY)
def add_staff():
    if request.method == 'POST':
        f = request.form
        new = database.execute(
            """INSERT INTO staff (full_name, designation, slmc_regno, qualification, station)
               VALUES (%s,%s,%s,%s,%s) RETURNING staff_id""",
            (f['full_name'], f['designation'], f.get('slmc_regno'), f.get('qualification'),
             f.get('station')), returning=True
        )
        database.log_action(current_user.id, 'INSERT', 'staff', new['staff_id'], None, 'Staff member added')
        flash('Staff member added.', 'success')
        return redirect(url_for('staff.list_staff'))
    return render_template('staff/form.html', record=None, action='Add', designations=DESIGNATIONS)


@staff_bp.route('/<int:sid>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(*ADMIN_ONLY)
def edit_staff(sid):
    record = database.fetchone("SELECT * FROM staff WHERE staff_id=%s", (sid,))
    if not record:
        flash('Staff member not found.', 'danger')
        return redirect(url_for('staff.list_staff'))
    if request.method == 'POST':
        f = request.form
        database.execute(
            """UPDATE staff SET full_name=%s, designation=%s, slmc_regno=%s,
               qualification=%s, station=%s WHERE staff_id=%s""",
            (f['full_name'], f['designation'], f.get('slmc_regno'), f.get('qualification'),
             f.get('station'), sid)
        )
        database.log_action(current_user.id, 'UPDATE', 'staff', sid, None, 'Staff member updated')
        flash('Staff member updated.', 'success')
        return redirect(url_for('staff.list_staff'))
    return render_template('staff/form.html', record=record, action='Edit', designations=DESIGNATIONS)


@staff_bp.route('/<int:sid>/delete', methods=['POST'])
@login_required
@roles_required(*ADMIN_ONLY)
def delete_staff(sid):
    database.execute("DELETE FROM staff WHERE staff_id=%s", (sid,))
    database.log_action(current_user.id, 'DELETE', 'staff', sid, None, 'Staff member deleted')
    flash('Staff member deleted.', 'warning')
    return redirect(url_for('staff.list_staff'))
