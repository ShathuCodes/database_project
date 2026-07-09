from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required, ALL_ROLES, CLINICAL
from app import database

cases_bp = Blueprint('cases', __name__)

CASE_TYPES = ['Assault', 'Sexual Assault', 'Homicide', 'Natural/Accidental Death', 'Skeletal Remains']
STATUSES   = ['Under Examination', 'Awaiting Lab', 'Report Pending', 'Despatched']


def _lookups():
    return dict(
        patients         = database.fetchall("SELECT patient_id, full_name FROM patient ORDER BY full_name"),
        police_stations  = database.fetchall("SELECT police_station_id, station_name FROM police_station ORDER BY station_name"),
        officers         = database.fetchall("SELECT officer_id, name, rank, police_station_id FROM investigating_officer ORDER BY name"),
        courts           = database.fetchall("SELECT court_id, court_name FROM court ORDER BY court_name"),
        magistrates      = database.fetchall("SELECT magistrate_id, name, court_id FROM magistrate ORDER BY name"),
        staff_list       = database.fetchall("SELECT staff_id, full_name, designation FROM staff ORDER BY full_name"),
    )


@cases_bp.route('/')
@login_required
@roles_required(*ALL_ROLES)
def list_cases():
    search     = request.args.get('search', '').strip()
    case_type  = request.args.get('case_type', '')
    status     = request.args.get('status', '')
    date_from  = request.args.get('date_from', '')
    date_to    = request.args.get('date_to', '')

    sql    = """SELECT cm.*, p.full_name AS patient_name
                FROM case_master cm
                LEFT JOIN patient p ON p.patient_id = cm.patient_id
                WHERE 1=1"""
    params = []

    if search:
        sql += " AND (cm.case_number ILIKE %s OR cm.police_refno ILIKE %s OR p.full_name ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    if case_type:
        sql += " AND cm.case_type = %s"
        params.append(case_type)
    if status:
        sql += " AND cm.status = %s"
        params.append(status)
    if date_from:
        sql += " AND cm.incident_date >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND cm.incident_date <= %s"
        params.append(date_to)

    sql += " ORDER BY cm.created_at DESC"
    cases = database.fetchall(sql, params)
    return render_template('cases/list.html', cases=cases,
                           case_types=CASE_TYPES, statuses=STATUSES,
                           search=search, case_type=case_type,
                           status=status, date_from=date_from, date_to=date_to)


@cases_bp.route('/<int:cid>')
@login_required
@roles_required(*ALL_ROLES)
def view_case(cid):
    case = database.fetchone(
        """SELECT cm.*, p.full_name AS patient_name, p.nic_passportno, p.gender, p.dob, p.age,
                  ps.station_name, io1.name AS issuing_officer_name, io2.name AS producing_officer_name,
                  c.court_name, m.name AS magistrate_name
           FROM case_master cm
           LEFT JOIN patient p ON p.patient_id = cm.patient_id
           LEFT JOIN police_station ps ON ps.police_station_id = cm.police_station_id
           LEFT JOIN investigating_officer io1 ON io1.officer_id = cm.issuing_officer_id
           LEFT JOIN investigating_officer io2 ON io2.officer_id = cm.producing_officer_id
           LEFT JOIN court c ON c.court_id = cm.court_id
           LEFT JOIN magistrate m ON m.magistrate_id = cm.magistrate_id
           WHERE cm.case_id = %s""", (cid,)
    )
    if not case:
        flash('Case not found.', 'danger')
        return redirect(url_for('cases.list_cases'))

    events = database.fetchall(
        """SELECT ce.*, s.full_name AS staff_name FROM case_event ce
           JOIN staff s ON s.staff_id = ce.staff_id
           WHERE ce.case_id=%s ORDER BY ce.event_date DESC""", (cid,)
    )
    assigned_staff = database.fetchall(
        """SELECT ca.role_in_case, s.staff_id, s.full_name, s.designation
           FROM case_assignment ca JOIN staff s ON s.staff_id = ca.staff_id
           WHERE ca.case_id=%s""", (cid,)
    )
    specimens = database.fetchall(
        """SELECT sp.*, ce.event_type FROM specimen sp
           JOIN case_event ce ON ce.event_id = sp.event_id
           WHERE ce.case_id=%s ORDER BY sp.collection_date DESC""", (cid,)
    )
    reports = database.fetchall(
        """SELECT r.*, s.full_name AS prepared_by_name FROM report r
           JOIN staff s ON s.staff_id = r.prepared_by_staff_id
           WHERE r.case_id=%s ORDER BY r.date_issued DESC""", (cid,)
    )
    verdict = database.fetchone(
        """SELECT iv.*, m.name AS magistrate_name FROM inquest_verdict iv
           JOIN magistrate m ON m.magistrate_id = iv.magistrate_id
           WHERE iv.case_id=%s""", (cid,)
    )
    return render_template('cases/view.html', case=case, events=events,
                           assigned_staff=assigned_staff, specimens=specimens,
                           reports=reports, verdict=verdict)


@cases_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required(*CLINICAL)
def add_case():
    lookups = _lookups()

    if request.method == 'POST':
        f = request.form
        case_number = f.get('case_number', '').strip()
        if not case_number:
            last = database.fetchone("SELECT case_number FROM case_master ORDER BY case_id DESC LIMIT 1")
            if last:
                try:
                    num = int(last['case_number'].split('/')[-1]) + 1
                except ValueError:
                    num = 1
            else:
                num = 1
            case_number = f"MLC/{__import__('datetime').date.today().year}/{num:04d}"

        new = database.execute(
            """INSERT INTO case_master
               (case_number, inquest_no, case_type, police_refno, court_refno, dept_refno,
                incident_date, trial_date, status, patient_id, police_station_id,
                issuing_officer_id, producing_officer_id, court_id, magistrate_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING case_id""",
            (case_number, f.get('inquest_no') or None, f['case_type'],
             f.get('police_refno'), f.get('court_refno'), f.get('dept_refno'),
             f.get('incident_date') or None, f.get('trial_date') or None,
             f.get('status', 'Under Examination'), f.get('patient_id') or None,
             f['police_station_id'], f.get('issuing_officer_id') or None,
             f.get('producing_officer_id') or None, f['court_id'],
             f.get('magistrate_id') or None),
            returning=True
        )
        cid = new['case_id']
        for sid in request.form.getlist('staff_ids'):
            database.execute(
                "INSERT INTO case_assignment (case_id, staff_id, role_in_case) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                (cid, sid, request.form.get(f'role_for_{sid}', 'Examining Officer'))
            )
        database.log_action(current_user.id, 'INSERT', 'case_master', cid, None, f'Case {case_number} created')
        flash(f'Case {case_number} created.', 'success')
        return redirect(url_for('cases.view_case', cid=cid))

    return render_template('cases/form.html', case=None, action='Add',
                           case_types=CASE_TYPES, statuses=STATUSES, **lookups)


@cases_bp.route('/<int:cid>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(*CLINICAL)
def edit_case(cid):
    case = database.fetchone("SELECT * FROM case_master WHERE case_id=%s", (cid,))
    if not case:
        flash('Case not found.', 'danger')
        return redirect(url_for('cases.list_cases'))

    lookups = _lookups()

    if request.method == 'POST':
        f = request.form
        database.execute(
            """UPDATE case_master SET inquest_no=%s, case_type=%s, police_refno=%s,
               court_refno=%s, dept_refno=%s, incident_date=%s, trial_date=%s, status=%s,
               patient_id=%s, police_station_id=%s, issuing_officer_id=%s,
               producing_officer_id=%s, court_id=%s, magistrate_id=%s
               WHERE case_id=%s""",
            (f.get('inquest_no') or None, f['case_type'], f.get('police_refno'),
             f.get('court_refno'), f.get('dept_refno'), f.get('incident_date') or None,
             f.get('trial_date') or None, f.get('status'), f.get('patient_id') or None,
             f['police_station_id'], f.get('issuing_officer_id') or None,
             f.get('producing_officer_id') or None, f['court_id'],
             f.get('magistrate_id') or None, cid)
        )
        database.execute("DELETE FROM case_assignment WHERE case_id=%s", (cid,))
        for sid in request.form.getlist('staff_ids'):
            database.execute(
                "INSERT INTO case_assignment (case_id, staff_id, role_in_case) VALUES (%s,%s,%s)",
                (cid, sid, request.form.get(f'role_for_{sid}', 'Examining Officer'))
            )
        database.log_action(current_user.id, 'UPDATE', 'case_master', cid, None, 'Case updated')
        flash('Case updated.', 'success')
        return redirect(url_for('cases.view_case', cid=cid))

    assigned_staff_ids = [
        str(r['staff_id']) for r in
        database.fetchall("SELECT staff_id FROM case_assignment WHERE case_id=%s", (cid,))
    ]
    return render_template('cases/form.html', case=case, action='Edit',
                           case_types=CASE_TYPES, statuses=STATUSES,
                           assigned_staff_ids=assigned_staff_ids, **lookups)


@cases_bp.route('/<int:cid>/delete', methods=['POST'])
@login_required
@roles_required(*CLINICAL)
def delete_case(cid):
    database.execute("DELETE FROM case_master WHERE case_id=%s", (cid,))
    database.log_action(current_user.id, 'DELETE', 'case_master', cid, None, 'Case deleted')
    flash('Case deleted.', 'warning')
    return redirect(url_for('cases.list_cases'))


@cases_bp.route('/<int:cid>/verdict', methods=['POST'])
@login_required
@roles_required(*CLINICAL)
def add_verdict(cid):
    f = request.form
    existing = database.fetchone("SELECT verdict_id FROM inquest_verdict WHERE case_id=%s", (cid,))
    if existing:
        database.execute(
            "UPDATE inquest_verdict SET magistrate_id=%s, verdict_text=%s, verdict_date=%s WHERE case_id=%s",
            (f['magistrate_id'], f.get('verdict_text'), f.get('verdict_date') or None, cid)
        )
    else:
        database.execute(
            "INSERT INTO inquest_verdict (case_id, magistrate_id, verdict_text, verdict_date) VALUES (%s,%s,%s,%s)",
            (cid, f['magistrate_id'], f.get('verdict_text'), f.get('verdict_date') or None)
        )
    flash('Inquest verdict recorded.', 'success')
    return redirect(url_for('cases.view_case', cid=cid))
