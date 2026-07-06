from flask import Blueprint, render_template, request, redirect, url_for, flash
# pyrefly: ignore [missing-import]
from flask_login import login_required, current_user
from app.helpers import roles_required
from app import database

evidence_bp = Blueprint('evidence', __name__)

EV_STATUSES = ['In Storage','Sent to Lab','Returned','Disposed']


@evidence_bp.route('/')
@login_required
def list_evidence():
    search  = request.args.get('search','').strip()
    status  = request.args.get('status','')
    case_id = request.args.get('case_id','')

    sql = """SELECT e.*, fc.case_number FROM evidence e
             JOIN forensic_case fc ON fc.case_id = e.case_id WHERE 1=1"""
    params = []
    if search:
        sql += " AND (e.evidence_type ILIKE %s OR e.description ILIKE %s OR fc.case_number ILIKE %s)"
        params.extend([f'%{search}%']*3)
    if status:
        sql += " AND e.status = %s"
        params.append(status)
    if case_id:
        sql += " AND e.case_id = %s"
        params.append(case_id)
    sql += " ORDER BY e.created_at DESC"
    records = database.fetchall(sql, params)
    cases   = database.fetchall("SELECT case_id, case_number FROM forensic_case ORDER BY case_id DESC")
    return render_template('evidence/list.html', records=records,
                           ev_statuses=EV_STATUSES, cases=cases,
                           search=search, status=status, case_id=case_id)


@evidence_bp.route('/add', methods=['GET','POST'])
@login_required
@roles_required('Hospital Management')
def add_evidence():
    cases = database.fetchall("SELECT case_id, case_number FROM forensic_case ORDER BY case_id DESC")
    if request.method == 'POST':
        f = request.form
        database.execute(
            """INSERT INTO evidence
               (case_id, evidence_type, description, storage_location,
                collected_by, collected_date, chain_of_custody, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['case_id'], f['evidence_type'], f.get('description'),
             f.get('storage_location'), f.get('collected_by'),
             f.get('collected_date') or None, f.get('chain_of_custody'),
             f.get('status','In Storage'))
        )
        database.log_action(current_user.id, 'INSERT', 'evidence')
        flash('Evidence record added.', 'success')
        return redirect(url_for('evidence.list_evidence'))
    return render_template('evidence/form.html', record=None, action='Add',
                           cases=cases, ev_statuses=EV_STATUSES)


@evidence_bp.route('/<int:eid>/edit', methods=['GET','POST'])
@login_required
@roles_required('Hospital Management')
def edit_evidence(eid):
    record = database.fetchone("SELECT * FROM evidence WHERE evidence_id=%s", (eid,))
    cases  = database.fetchall("SELECT case_id, case_number FROM forensic_case ORDER BY case_id DESC")
    if request.method == 'POST':
        f = request.form
        database.execute(
            """UPDATE evidence SET case_id=%s, evidence_type=%s, description=%s,
               storage_location=%s, collected_by=%s, collected_date=%s,
               chain_of_custody=%s, status=%s WHERE evidence_id=%s""",
            (f['case_id'], f['evidence_type'], f.get('description'),
             f.get('storage_location'), f.get('collected_by'),
             f.get('collected_date') or None, f.get('chain_of_custody'),
             f.get('status'), eid)
        )
        database.log_action(current_user.id, 'UPDATE', 'evidence', eid)
        flash('Evidence updated.', 'success')
        return redirect(url_for('evidence.list_evidence'))
    return render_template('evidence/form.html', record=record, action='Edit',
                           cases=cases, ev_statuses=EV_STATUSES)


@evidence_bp.route('/<int:eid>/delete', methods=['POST'])
@login_required
@roles_required('Hospital Management')
def delete_evidence(eid):
    database.execute("DELETE FROM evidence WHERE evidence_id=%s", (eid,))
    flash('Evidence deleted.', 'warning')
    return redirect(url_for('evidence.list_evidence'))