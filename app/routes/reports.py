from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from app.helpers import roles_required, ALL_ROLES, CLINICAL
from app import database

reports_bp = Blueprint('reports', __name__)

REPORT_TYPES = ['MLR', 'PMR', 'Court Report']
STATUSES = ['Draft', 'Signed', 'Despatched']


@reports_bp.route('/')
@login_required
@roles_required(*ALL_ROLES)
def list_reports():
    search       = request.args.get('search', '').strip()
    report_type  = request.args.get('report_type', '')
    status       = request.args.get('status', '')

    sql = """SELECT r.*, cm.case_number, s.full_name AS prepared_by_name
             FROM report r
             JOIN case_master cm ON cm.case_id = r.case_id
             JOIN staff s ON s.staff_id = r.prepared_by_staff_id
             WHERE 1=1"""
    params = []
    if search:
        sql += " AND (cm.case_number ILIKE %s OR r.serial_no ILIKE %s)"
        params.extend([f'%{search}%'] * 2)
    if report_type:
        sql += " AND r.report_type = %s"
        params.append(report_type)
    if status:
        sql += " AND r.status = %s"
        params.append(status)
    sql += " ORDER BY r.date_issued DESC NULLS LAST"
    reports = database.fetchall(sql, params)
    return render_template('reports/list.html', reports=reports, report_types=REPORT_TYPES,
                           statuses=STATUSES, search=search, report_type=report_type, status=status)


@reports_bp.route('/<int:rid>/view')
@login_required
@roles_required(*ALL_ROLES)
def view_report(rid):
    report = database.fetchone(
        """SELECT r.*, cm.case_number, cm.inquest_no, cm.case_type, cm.police_refno, cm.court_refno,
                  cm.dept_refno, cm.incident_date, cm.received_date, cm.status AS case_status,
                  p.full_name AS patient_name, p.nic_passportno AS patient_nic, p.age AS patient_age,
                  p.gender AS patient_gender, p.address AS patient_address, p.occupation AS patient_occupation,
                  ps.station_name AS police_station, c.court_name, m.name AS magistrate_name,
                  s.full_name AS prepared_by_name, s.designation AS staff_designation,
                  s.slmc_regno, s.station AS staff_station
           FROM report r
           JOIN case_master cm ON cm.case_id = r.case_id
           LEFT JOIN patient p ON p.patient_id = cm.patient_id
           LEFT JOIN police_station ps ON ps.police_station_id = cm.police_station_id
           LEFT JOIN court c ON c.court_id = cm.court_id
           LEFT JOIN magistrate m ON m.magistrate_id = cm.magistrate_id
           LEFT JOIN staff s ON s.staff_id = r.prepared_by_staff_id
           WHERE r.report_id = %s""", (rid,)
    )
    if not report:
        flash('Report not found.', 'danger')
        return redirect(url_for('reports.list_reports'))

    # Fetch Event details
    event = None
    clinical = None
    postmortem = None
    skeletal = None
    injuries = []
    organs = []

    if report['event_id']:
        event = database.fetchone("SELECT * FROM case_event WHERE event_id = %s", (report['event_id'],))
        if event:
            if event['event_type'] == 'Clinical Examination':
                clinical = database.fetchone("SELECT * FROM clinical_examination WHERE event_id = %s", (event['event_id'],))
            elif event['event_type'] == 'Postmortem':
                postmortem = database.fetchone("SELECT * FROM postmortem WHERE event_id = %s", (event['event_id'],))
                organs = database.fetchall("SELECT * FROM postmortem_organ_finding WHERE event_id = %s", (event['event_id'],))
            elif event['event_type'] == 'Skeletal Examination':
                skeletal = database.fetchone("SELECT * FROM skeletal_examination WHERE event_id = %s", (event['event_id'],))

        injuries = database.fetchall(
            """SELECT inj.*, gh.description AS grievous_clause_desc
               FROM injury inj
               LEFT JOIN grievous_hurt_type gh ON gh.clause_code = inj.grievous_hurt_clause_code
               WHERE inj.event_id = %s""", (report['event_id'],)
        )

    return render_template('reports/view.html', report=report, event=event, clinical=clinical,
                           postmortem=postmortem, skeletal=skeletal, injuries=injuries, organs=organs)


@reports_bp.route('/<int:rid>/download-txt')
@login_required
@roles_required(*ALL_ROLES)
def download_txt(rid):
    report = database.fetchone(
        """SELECT r.*, cm.case_number, cm.case_type, p.full_name AS patient_name,
                  s.full_name AS prepared_by_name, s.slmc_regno, s.station AS staff_station
           FROM report r
           JOIN case_master cm ON cm.case_id = r.case_id
           LEFT JOIN patient p ON p.patient_id = cm.patient_id
           LEFT JOIN staff s ON s.staff_id = r.prepared_by_staff_id
           WHERE r.report_id = %s""", (rid,)
    )
    if not report:
        flash('Report not found.', 'danger')
        return redirect(url_for('reports.list_reports'))

    content = f"""================================================================================
OFFICIAL FORENSIC MEDICO-LEGAL REPORT
DEPARTMENT OF FORENSIC MEDICINE & MEDICO-LEGAL SERVICES
================================================================================

REPORT TYPE        : {report['report_type']}
SERIAL NUMBER      : {report['serial_no'] or 'N/A'}
CASE NUMBER        : {report['case_number']}
CASE TYPE          : {report['case_type']}
PATIENT / SUBJECT  : {report['patient_name'] or 'N/A'}
ISSUING OFFICER    : {report['prepared_by_name']} (SLMC Reg: {report['slmc_regno'] or 'N/A'})
STATION            : {report['staff_station'] or 'N/A'}
DATE ISSUED        : {report['date_issued'].strftime('%Y-%m-%d %H:%M') if report['date_issued'] else 'N/A'}
STATUS             : {report['status']}

--------------------------------------------------------------------------------
SUMMARY & CONCLUSION
--------------------------------------------------------------------------------
This report serves as an official medico-legal record issued for judicial
and investigative proceedings. All examination findings, injury classifications,
and medical opinions documented herein are verified under SLMC regulations.

Prepared By: {report['prepared_by_name']}
Signature  : ___________________________
Date       : {report['date_issued'].strftime('%Y-%m-%d') if report['date_issued'] else 'N/A'}
================================================================================
"""
    filename = f"Report_{report['case_number'].replace('/', '_')}_{report['report_type']}.txt"
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@reports_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required(*CLINICAL)
def add_report():
    cases = database.fetchall("SELECT case_id, case_number FROM case_master ORDER BY case_id DESC")
    staff = database.fetchall("SELECT staff_id, full_name FROM staff ORDER BY full_name")
    events = database.fetchall(
        """SELECT ce.event_id, ce.event_type, ce.case_id, cm.case_number
           FROM case_event ce JOIN case_master cm ON cm.case_id = ce.case_id
           ORDER BY ce.event_id DESC""")

    if request.method == 'POST':
        f = request.form
        new = database.execute(
            """INSERT INTO report (serial_no, case_id, event_id, report_type,
               prepared_by_staff_id, date_issued, date_despatched, status, file_path)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING report_id""",
            (f.get('serial_no'), f['case_id'], f.get('event_id') or None, f['report_type'],
             f['prepared_by_staff_id'], f.get('date_issued') or None,
             f.get('date_despatched') or None, f.get('status', 'Draft'), f.get('file_path')),
            returning=True
        )
        database.log_action(current_user.id, 'INSERT', 'report', new['report_id'], None, 'Report created')
        flash('Report created.', 'success')
        return redirect(url_for('reports.list_reports'))

    return render_template('reports/form.html', record=None, action='Add', cases=cases, staff=staff,
                           events=events, report_types=REPORT_TYPES, statuses=STATUSES)


@reports_bp.route('/<int:rid>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(*CLINICAL)
def edit_report(rid):
    record = database.fetchone("SELECT * FROM report WHERE report_id=%s", (rid,))
    if not record:
        flash('Report not found.', 'danger')
        return redirect(url_for('reports.list_reports'))
    cases = database.fetchall("SELECT case_id, case_number FROM case_master ORDER BY case_id DESC")
    staff = database.fetchall("SELECT staff_id, full_name FROM staff ORDER BY full_name")
    events = database.fetchall(
        """SELECT ce.event_id, ce.event_type, ce.case_id, cm.case_number
           FROM case_event ce JOIN case_master cm ON cm.case_id = ce.case_id
           ORDER BY ce.event_id DESC""")

    if request.method == 'POST':
        f = request.form
        database.execute(
            """UPDATE report SET serial_no=%s, case_id=%s, event_id=%s, report_type=%s,
               prepared_by_staff_id=%s, date_issued=%s, date_despatched=%s, status=%s, file_path=%s
               WHERE report_id=%s""",
            (f.get('serial_no'), f['case_id'], f.get('event_id') or None, f['report_type'],
             f['prepared_by_staff_id'], f.get('date_issued') or None,
             f.get('date_despatched') or None, f.get('status'), f.get('file_path'), rid)
        )
        if f.get('status') == 'Despatched':
            database.execute("UPDATE case_master SET status='Despatched' WHERE case_id=%s", (f['case_id'],))
        database.log_action(current_user.id, 'UPDATE', 'report', rid, None, 'Report updated')
        flash('Report updated.', 'success')
        return redirect(url_for('reports.list_reports'))

    return render_template('reports/form.html', record=record, action='Edit', cases=cases, staff=staff,
                           events=events, report_types=REPORT_TYPES, statuses=STATUSES)


@reports_bp.route('/<int:rid>/delete', methods=['POST'])
@login_required
@roles_required(*CLINICAL)
def delete_report(rid):
    database.execute("DELETE FROM report WHERE report_id=%s", (rid,))
    database.log_action(current_user.id, 'DELETE', 'report', rid, None, 'Report deleted')
    flash('Report deleted.', 'warning')
    return redirect(url_for('reports.list_reports'))
