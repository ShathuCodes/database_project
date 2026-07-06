from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required
from app import database

lab_bp = Blueprint('lab', __name__)

LAB_STATUSES = ['Pending','Completed','Failed']


@lab_bp.route('/')
@login_required
@roles_required('Hospital Management')
def list_tests():
    search = request.args.get('search','').strip()
    status = request.args.get('status','')
    sql = """SELECT lt.*, fc.case_number, s.full_name AS requested_by_name
             FROM lab_test lt
             JOIN forensic_case fc ON fc.case_id=lt.case_id
             LEFT JOIN staff s ON s.staff_id=lt.requested_by
             WHERE 1=1"""
    params=[]
    if search:
        sql += " AND (lt.test_type ILIKE %s OR fc.case_number ILIKE %s)"
        params.extend([f'%{search}%']*2)
    if status:
        sql += " AND lt.status=%s"
        params.append(status)
    sql += " ORDER BY lt.created_at DESC"
    records = database.fetchall(sql,params)
    return render_template('lab/list.html', records=records,
                           lab_statuses=LAB_STATUSES, search=search, status=status)


@lab_bp.route('/add', methods=['GET','POST'])
@login_required
@roles_required('Hospital Management')
def add_test():
    cases    = database.fetchall("SELECT case_id, case_number FROM forensic_case ORDER BY case_id DESC")
    evidence = database.fetchall("SELECT evidence_id, evidence_type, case_id FROM evidence")
    staff    = database.fetchall("SELECT staff_id, full_name FROM staff WHERE role IN ('Doctor','JMO','Lab Staff')")
    if request.method == 'POST':
        f = request.form
        database.execute(
            """INSERT INTO lab_test
               (case_id, evidence_id, test_type, requested_by, tested_by, test_date, result, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['case_id'], f.get('evidence_id') or None, f['test_type'],
             f.get('requested_by') or None, f.get('tested_by'),
             f.get('test_date') or None, f.get('result'),
             f.get('status','Pending'))
        )
        database.log_action(current_user.id,'INSERT','lab_test')
        flash('Lab test added.','success')
        return redirect(url_for('lab.list_tests'))
    return render_template('lab/form.html', record=None, action='Add',
                           cases=cases, evidence=evidence, staff=staff,
                           lab_statuses=LAB_STATUSES)


@lab_bp.route('/<int:tid>/edit', methods=['GET','POST'])
@login_required
@roles_required('Hospital Management')
def edit_test(tid):
    record   = database.fetchone("SELECT * FROM lab_test WHERE test_id=%s",(tid,))
    cases    = database.fetchall("SELECT case_id, case_number FROM forensic_case ORDER BY case_id DESC")
    evidence = database.fetchall("SELECT evidence_id, evidence_type, case_id FROM evidence")
    staff    = database.fetchall("SELECT staff_id, full_name FROM staff WHERE role IN ('Doctor','JMO','Lab Staff')")
    if request.method == 'POST':
        f = request.form
        database.execute(
            """UPDATE lab_test SET case_id=%s, evidence_id=%s, test_type=%s,
               requested_by=%s, tested_by=%s, test_date=%s, result=%s, status=%s
               WHERE test_id=%s""",
            (f['case_id'], f.get('evidence_id') or None, f['test_type'],
             f.get('requested_by') or None, f.get('tested_by'),
             f.get('test_date') or None, f.get('result'), f.get('status'), tid)
        )
        database.log_action(current_user.id,'UPDATE','lab_test',tid)
        flash('Lab test updated.','success')
        return redirect(url_for('lab.list_tests'))
    return render_template('lab/form.html', record=record, action='Edit',
                           cases=cases, evidence=evidence, staff=staff,
                           lab_statuses=LAB_STATUSES)


@lab_bp.route('/<int:tid>/delete', methods=['POST'])
@login_required
@roles_required('Hospital Management')
def delete_test(tid):
    database.execute("DELETE FROM lab_test WHERE test_id=%s",(tid,))
    flash('Test deleted.','warning')
    return redirect(url_for('lab.list_tests'))