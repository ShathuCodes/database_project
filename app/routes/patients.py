from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required
from app import database

patients_bp = Blueprint('patients', __name__)

ALLOWED_VIEW  = ('Admin', 'Doctor', 'JMO', 'Clerk')
ALLOWED_EDIT  = ('Admin', 'Clerk')


@patients_bp.route('/')
@login_required
@roles_required('Hospital Management')
def list_patients():
    search = request.args.get('search', '').strip()
    gender = request.args.get('gender', '')

    sql    = "SELECT * FROM patient WHERE 1=1"
    params = []

    if search:
        sql += " AND (full_name ILIKE %s OR nic ILIKE %s OR hospital_no ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    if gender:
        sql += " AND gender = %s"
        params.append(gender)

    sql += " ORDER BY created_at DESC"
    patients = database.fetchall(sql, params)
    return render_template('patients/list.html', patients=patients,
                           search=search, gender=gender)


@patients_bp.route('/<int:pid>')
@login_required
@roles_required('Hospital Management')
def view_patient(pid):
    patient = database.fetchone("SELECT * FROM patient WHERE patient_id=%s", (pid,))
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.list_patients'))
    cases = database.fetchall(
        "SELECT * FROM forensic_case WHERE patient_id=%s ORDER BY created_at DESC", (pid,)
    )
    return render_template('patients/view.html', patient=patient, cases=cases)


@patients_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('Hospital Management')
def add_patient():
    if request.method == 'POST':
        f = request.form
        database.execute(
            """INSERT INTO patient (full_name, nic, dob, gender, address, contact, hospital_no)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (f['full_name'], f.get('nic') or None, f.get('dob') or None,
             f.get('gender'), f.get('address'), f.get('contact'), f.get('hospital_no'))
        )
        database.log_action(current_user.id, 'INSERT', 'patient', details='New patient added')
        flash('Patient registered successfully.', 'success')
        return redirect(url_for('patients.list_patients'))
    return render_template('patients/form.html', patient=None, action='Add')


@patients_bp.route('/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Hospital Management')
def edit_patient(pid):
    patient = database.fetchone("SELECT * FROM patient WHERE patient_id=%s", (pid,))
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.list_patients'))

    if request.method == 'POST':
        f = request.form
        database.execute(
            """UPDATE patient SET full_name=%s, nic=%s, dob=%s, gender=%s,
               address=%s, contact=%s, hospital_no=%s WHERE patient_id=%s""",
            (f['full_name'], f.get('nic') or None, f.get('dob') or None,
             f.get('gender'), f.get('address'), f.get('contact'),
             f.get('hospital_no'), pid)
        )
        database.log_action(current_user.id, 'UPDATE', 'patient', pid, 'Patient updated')
        flash('Patient updated.', 'success')
        return redirect(url_for('patients.view_patient', pid=pid))

    return render_template('patients/form.html', patient=patient, action='Edit')


@patients_bp.route('/<int:pid>/delete', methods=['POST'])
@login_required
@roles_required('Hospital Management')
def delete_patient(pid):
    database.execute("DELETE FROM patient WHERE patient_id=%s", (pid,))
    database.log_action(current_user.id, 'DELETE', 'patient', pid, 'Patient deleted')
    flash('Patient deleted.', 'warning')
    return redirect(url_for('patients.list_patients'))