from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required
from app import database

cases_bp = Blueprint('cases', __name__)

CASE_TYPES = ['Postmortem','Assault','Accident','Sexual Assault','Toxicology','Clinical']
STATUSES   = ['Open','In Progress','Closed']


@cases_bp.route('/')
@login_required
def list_cases():
    search     = request.args.get('search', '').strip()
    case_type  = request.args.get('case_type', '')
    status     = request.args.get('status', '')
    date_from  = request.args.get('date_from', '')
    date_to    = request.args.get('date_to', '')

    sql    = """SELECT fc.*, p.full_name AS patient_name
                FROM forensic_case fc
                LEFT JOIN patient p ON p.patient_id = fc.patient_id
                WHERE 1=1"""
    params = []

    if search:
        sql += " AND (fc.case_number ILIKE %s OR fc.police_ref ILIKE %s OR p.full_name ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    if case_type:
        sql += " AND fc.case_type = %s"
        params.append(case_type)
    if status:
        sql += " AND fc.status = %s"
        params.append(status)
    if date_from:
        sql += " AND fc.incident_date >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND fc.incident_date <= %s"
        params.append(date_to)

    sql += " ORDER BY fc.created_at DESC"
    cases = database.fetchall(sql, params)
    return render_template('cases/list.html', cases=cases,
                           case_types=CASE_TYPES, statuses=STATUSES,
                           search=search, case_type=case_type,
                           status=status, date_from=date_from, date_to=date_to)


@cases_bp.route('/<int:cid>')
@login_required
def view_case(cid):
    case = database.fetchone(
        """SELECT fc.*, p.full_name AS patient_name, p.nic, p.gender, p.dob
           FROM forensic_case fc
           LEFT JOIN patient p ON p.patient_id = fc.patient_id
           WHERE fc.case_id = %s""", (cid,)
    )
    if not case:
        flash('Case not found.', 'danger')
        return redirect(url_for('cases.list_cases'))

    postmortems = database.fetchall(
        "SELECT pm.*, s.full_name AS doctor_name FROM postmortem pm LEFT JOIN staff s ON s.staff_id=pm.doctor_id WHERE pm.case_id=%s", (cid,)
    )
    evidence = database.fetchall(
        "SELECT * FROM evidence WHERE case_id=%s ORDER BY collected_date DESC", (cid,)
    )
    lab_tests = database.fetchall(
        "SELECT lt.*, s.full_name AS requested_by_name FROM lab_test lt LEFT JOIN staff s ON s.staff_id=lt.requested_by WHERE lt.case_id=%s", (cid,)
    )
    reports = database.fetchall(
        "SELECT cr.*, s.full_name AS doctor_name FROM court_report cr LEFT JOIN staff s ON s.staff_id=cr.doctor_id WHERE cr.case_id=%s", (cid,)
    )
    doctors = database.fetchall(
        """SELECT s.staff_id, s.full_name FROM case_doctor cd
           JOIN staff s ON s.staff_id=cd.staff_id WHERE cd.case_id=%s""", (cid,)
    )
    return render_template('cases/view.html', case=case,
                           postmortems=postmortems, evidence=evidence,
                           lab_tests=lab_tests, reports=reports, doctors=doctors)


@cases_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('Hospital Management')
def add_case():
    patients = database.fetchall("SELECT patient_id, full_name FROM patient ORDER BY full_name")
    doctors  = database.fetchall("SELECT staff_id, full_name FROM staff WHERE role IN ('Doctor','JMO') ORDER BY full_name")

    if request.method == 'POST':
        f = request.form
        # Auto-generate case number if blank
        case_number = f.get('case_number','').strip()
        if not case_number:
            last = database.fetchone("SELECT case_number FROM forensic_case ORDER BY case_id DESC LIMIT 1")
            if last:
                num = int(last['case_number'].split('-')[-1]) + 1
            else:
                num = 1
            case_number = f"FC-{__import__('datetime').date.today().year}-{num:03d}"

        new = database.execute(
            """INSERT INTO forensic_case
               (patient_id, case_number, case_type, incident_date, police_ref,
                court_ref, police_station, magistrate, status, description, created_by)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING case_id""",
            (f['patient_id'], case_number, f['case_type'],
             f.get('incident_date') or None, f.get('police_ref'),
             f.get('court_ref'), f.get('police_station'), f.get('magistrate'),
             f.get('status','Open'), f.get('description'), current_user.id),
            returning=True
        )
        cid = new['case_id']
        # Assign doctors
        for did in request.form.getlist('doctor_ids'):
            database.execute(
                "INSERT INTO case_doctor (case_id, staff_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                (cid, did)
            )
        database.log_action(current_user.id, 'INSERT', 'forensic_case', cid, f'Case {case_number} created')
        flash(f'Case {case_number} created.', 'success')
        return redirect(url_for('cases.view_case', cid=cid))

    return render_template('cases/form.html', case=None, action='Add',
                           patients=patients, doctors=doctors,
                           case_types=CASE_TYPES, statuses=STATUSES)


@cases_bp.route('/<int:cid>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Hospital Management')
def edit_case(cid):
    case = database.fetchone("SELECT * FROM forensic_case WHERE case_id=%s", (cid,))
    if not case:
        flash('Case not found.', 'danger')
        return redirect(url_for('cases.list_cases'))

    patients = database.fetchall("SELECT patient_id, full_name FROM patient ORDER BY full_name")
    doctors  = database.fetchall("SELECT staff_id, full_name FROM staff WHERE role IN ('Doctor','JMO') ORDER BY full_name")

    if request.method == 'POST':
        f = request.form
        database.execute(
            """UPDATE forensic_case SET patient_id=%s, case_type=%s, incident_date=%s,
               police_ref=%s, court_ref=%s, police_station=%s, magistrate=%s,
               status=%s, description=%s WHERE case_id=%s""",
            (f['patient_id'], f['case_type'], f.get('incident_date') or None,
             f.get('police_ref'), f.get('court_ref'), f.get('police_station'),
             f.get('magistrate'), f.get('status'), f.get('description'), cid)
        )
        # Re-assign doctors
        database.execute("DELETE FROM case_doctor WHERE case_id=%s", (cid,))
        for did in request.form.getlist('doctor_ids'):
            database.execute(
                "INSERT INTO case_doctor (case_id, staff_id) VALUES (%s,%s)", (cid, did)
            )
        database.log_action(current_user.id, 'UPDATE', 'forensic_case', cid, 'Case updated')
        flash('Case updated.', 'success')
        return redirect(url_for('cases.view_case', cid=cid))

    assigned_doctor_ids = [
        str(r['staff_id']) for r in
        database.fetchall("SELECT staff_id FROM case_doctor WHERE case_id=%s", (cid,))
    ]
    return render_template('cases/form.html', case=case, action='Edit',
                           patients=patients, doctors=doctors,
                           case_types=CASE_TYPES, statuses=STATUSES,
                           assigned_doctor_ids=assigned_doctor_ids)


@cases_bp.route('/<int:cid>/delete', methods=['POST'])
@login_required
@roles_required('Hospital Management')
def delete_case(cid):
    database.execute("DELETE FROM forensic_case WHERE case_id=%s", (cid,))
    database.log_action(current_user.id, 'DELETE', 'forensic_case', cid, 'Case deleted')
    flash('Case deleted.', 'warning')
    return redirect(url_for('cases.list_cases'))