from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required
from app import database

reports_bp = Blueprint('reports', __name__)

RPT_STATUSES = ['Draft','Submitted','Accepted','Rejected']


@reports_bp.route('/')
@login_required
def list_reports():
    search = request.args.get('search','').strip()
    status = request.args.get('status','')
    sql = """SELECT cr.*, fc.case_number, s.full_name AS doctor_name
             FROM court_report cr
             JOIN forensic_case fc ON fc.case_id=cr.case_id
             LEFT JOIN staff s ON s.staff_id=cr.doctor_id WHERE 1=1"""
    params=[]
    if search:
        sql += " AND (fc.case_number ILIKE %s OR cr.court_name ILIKE %s)"
        params.extend([f'%{search}%']*2)
    if status:
        sql += " AND cr.status=%s"
        params.append(status)
    sql += " ORDER BY cr.created_at DESC"
    records = database.fetchall(sql,params)
    return render_template('reports/list.html', records=records,
                           rpt_statuses=RPT_STATUSES, search=search, status=status)


@reports_bp.route('/<int:rid>')
@login_required
def view_report(rid):
    report = database.fetchone(
        """SELECT cr.*, fc.case_number, fc.case_type, p.full_name AS patient_name,
                  s.full_name AS doctor_name
           FROM court_report cr
           JOIN forensic_case fc ON fc.case_id=cr.case_id
           LEFT JOIN patient p ON p.patient_id=fc.patient_id
           LEFT JOIN staff s ON s.staff_id=cr.doctor_id
           WHERE cr.report_id=%s""", (rid,)
    )
    return render_template('reports/view.html', report=report)


@reports_bp.route('/add', methods=['GET','POST'])
@login_required
@roles_required('Hospital Management')
def add_report():
    cases   = database.fetchall("SELECT case_id, case_number FROM forensic_case ORDER BY case_id DESC")
    doctors = database.fetchall("SELECT staff_id, full_name FROM staff WHERE role IN ('Doctor','JMO')")
    if request.method == 'POST':
        f = request.form
        new = database.execute(
            """INSERT INTO court_report
               (case_id, doctor_id, report_type, content, submission_date, court_name, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING report_id""",
            (f['case_id'], f.get('doctor_id') or None, f.get('report_type'),
             f.get('content'), f.get('submission_date') or None,
             f.get('court_name'), f.get('status','Draft')),
            returning=True
        )
        database.log_action(current_user.id,'INSERT','court_report',new['report_id'])
        flash('Court report created.','success')
        return redirect(url_for('reports.view_report', rid=new['report_id']))
    return render_template('reports/form.html', report=None, action='Add',
                           cases=cases, doctors=doctors, rpt_statuses=RPT_STATUSES)


@reports_bp.route('/<int:rid>/edit', methods=['GET','POST'])
@login_required
@roles_required('Hospital Management')
def edit_report(rid):
    report  = database.fetchone("SELECT * FROM court_report WHERE report_id=%s",(rid,))
    cases   = database.fetchall("SELECT case_id, case_number FROM forensic_case ORDER BY case_id DESC")
    doctors = database.fetchall("SELECT staff_id, full_name FROM staff WHERE role IN ('Doctor','JMO')")
    if request.method == 'POST':
        f = request.form
        database.execute(
            """UPDATE court_report SET case_id=%s, doctor_id=%s, report_type=%s,
               content=%s, submission_date=%s, court_name=%s, status=%s
               WHERE report_id=%s""",
            (f['case_id'], f.get('doctor_id') or None, f.get('report_type'),
             f.get('content'), f.get('submission_date') or None,
             f.get('court_name'), f.get('status'), rid)
        )
        database.log_action(current_user.id,'UPDATE','court_report',rid)
        flash('Report updated.','success')
        return redirect(url_for('reports.view_report', rid=rid))
    return render_template('reports/form.html', report=report, action='Edit',
                           cases=cases, doctors=doctors, rpt_statuses=RPT_STATUSES)


@reports_bp.route('/<int:rid>/delete', methods=['POST'])
@login_required
@roles_required('Hospital Management')
def delete_report(rid):
    database.execute("DELETE FROM court_report WHERE report_id=%s",(rid,))
    flash('Report deleted.','warning')
    return redirect(url_for('reports.list_reports'))