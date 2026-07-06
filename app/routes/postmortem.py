from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required
from app import database

postmortem_bp = Blueprint('postmortem', __name__)

MANNERS = ['Natural','Homicide','Suicide','Accident','Undetermined']

@postmortem_bp.route('/')
@login_required
@roles_required('Hospital Management')
def list_pm():
    search    = request.args.get('search','').strip()
    manner    = request.args.get('manner','')
    date_from = request.args.get('date_from','')

    sql = """SELECT pm.*, fc.case_number, p.full_name AS patient_name,
                    s.full_name AS doctor_name
             FROM postmortem pm
             JOIN forensic_case fc ON fc.case_id = pm.case_id
             LEFT JOIN patient p ON p.patient_id = fc.patient_id
             LEFT JOIN staff s ON s.staff_id = pm.doctor_id
             WHERE 1=1"""
    params = []
    if search:
        sql += " AND (fc.case_number ILIKE %s OR p.full_name ILIKE %s OR pm.cause_of_death ILIKE %s)"
        params.extend([f'%{search}%']*3)
    if manner:
        sql += " AND pm.manner_of_death = %s"
        params.append(manner)
    if date_from:
        sql += " AND pm.exam_date >= %s"
        params.append(date_from)
    sql += " ORDER BY pm.created_at DESC"
    records = database.fetchall(sql, params)
    return render_template('postmortem/list.html', records=records,
                           manners=MANNERS, search=search,
                           manner=manner, date_from=date_from)


@postmortem_bp.route('/add', methods=['GET','POST'])
@login_required
@roles_required('Hospital Management')
def add_pm():
    cases   = database.fetchall("SELECT case_id, case_number FROM forensic_case ORDER BY case_id DESC")
    doctors = database.fetchall("SELECT staff_id, full_name FROM staff WHERE role IN ('Doctor','JMO')")
    if request.method == 'POST':
        f = request.form
        database.execute(
            """INSERT INTO postmortem
               (case_id, doctor_id, exam_date, findings, cause_of_death,
                manner_of_death, body_condition, notes)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['case_id'], f.get('doctor_id') or None, f.get('exam_date') or None,
             f.get('findings'), f.get('cause_of_death'), f.get('manner_of_death'),
             f.get('body_condition'), f.get('notes'))
        )
        database.log_action(current_user.id, 'INSERT', 'postmortem')
        flash('Postmortem record added.', 'success')
        return redirect(url_for('postmortem.list_pm'))
    return render_template('postmortem/form.html', record=None, action='Add',
                           cases=cases, doctors=doctors, manners=MANNERS)


@postmortem_bp.route('/<int:pid>/edit', methods=['GET','POST'])
@login_required
@roles_required('Hospital Management')
def edit_pm(pid):
    record  = database.fetchone("SELECT * FROM postmortem WHERE pm_id=%s", (pid,))
    cases   = database.fetchall("SELECT case_id, case_number FROM forensic_case ORDER BY case_id DESC")
    doctors = database.fetchall("SELECT staff_id, full_name FROM staff WHERE role IN ('Doctor','JMO')")
    if request.method == 'POST':
        f = request.form
        database.execute(
            """UPDATE postmortem SET case_id=%s, doctor_id=%s, exam_date=%s,
               findings=%s, cause_of_death=%s, manner_of_death=%s,
               body_condition=%s, notes=%s WHERE pm_id=%s""",
            (f['case_id'], f.get('doctor_id') or None, f.get('exam_date') or None,
             f.get('findings'), f.get('cause_of_death'), f.get('manner_of_death'),
             f.get('body_condition'), f.get('notes'), pid)
        )
        database.log_action(current_user.id, 'UPDATE', 'postmortem', pid)
        flash('Postmortem record updated.', 'success')
        return redirect(url_for('postmortem.list_pm'))
    return render_template('postmortem/form.html', record=record, action='Edit',
                           cases=cases, doctors=doctors, manners=MANNERS)


@postmortem_bp.route('/<int:pid>/delete', methods=['POST'])
@login_required
@roles_required('Hospital Management')
def delete_pm(pid):
    database.execute("DELETE FROM postmortem WHERE pm_id=%s", (pid,))
    flash('Record deleted.', 'warning')
    return redirect(url_for('postmortem.list_pm'))