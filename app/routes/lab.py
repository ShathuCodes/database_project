from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required, ALL_ROLES, LAB_ROLES
from app import database

lab_bp = Blueprint('lab', __name__)

LAB_NAMES = ['Government Analyst', 'Histopathology', 'Microbiology', 'Medical Research Institute (MRI)']
URGENCY = ['Routine', 'Urgent', 'Storage']
PURPOSE = ['Judicial', 'Academic']


@lab_bp.route('/')
@login_required
@roles_required(*ALL_ROLES)
def list_requests():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')  # '', 'pending', 'completed'

    sql = """SELECT lr.*, sp.specimen_type, sp.specimen_label, cm.case_number,
                    lres.lab_result_id
             FROM lab_request lr
             JOIN specimen sp ON sp.specimen_id = lr.specimen_id
             JOIN case_event ce ON ce.event_id = sp.event_id
             JOIN case_master cm ON cm.case_id = ce.case_id
             LEFT JOIN lab_result lres ON lres.lab_request_id = lr.lab_request_id
             WHERE 1=1"""
    params = []
    if search:
        sql += " AND (cm.case_number ILIKE %s OR lr.test_requested ILIKE %s OR lr.lab_name ILIKE %s)"
        params.extend([f'%{search}%'] * 3)
    if status == 'pending':
        sql += " AND lres.lab_result_id IS NULL"
    elif status == 'completed':
        sql += " AND lres.lab_result_id IS NOT NULL"
    sql += " ORDER BY lr.date_sent DESC"
    requests_ = database.fetchall(sql, params)
    return render_template('lab/list.html', requests=requests_, search=search, status=status)


@lab_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required(*LAB_ROLES)
def add_request():
    specimens = database.fetchall(
        """SELECT sp.specimen_id, sp.specimen_type, sp.specimen_label, cm.case_number
           FROM specimen sp JOIN case_event ce ON ce.event_id = sp.event_id
           JOIN case_master cm ON cm.case_id = ce.case_id ORDER BY sp.specimen_id DESC""")
    staff = database.fetchall("SELECT staff_id, full_name FROM staff ORDER BY full_name")

    if request.method == 'POST':
        f = request.form
        new = database.execute(
            """INSERT INTO lab_request
               (specimen_id, lab_name, requested_by_staff_id, test_requested, poisons_suspected,
                macroscopic_appearances, special_procedure_request, date_sent, urgency,
                request_purpose, date_accepted, accepted_by_name, receiving_refno)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING lab_request_id""",
            (f['specimen_id'], f['lab_name'], f['requested_by_staff_id'], f.get('test_requested'),
             f.get('poisons_suspected'), f.get('macroscopic_appearances'),
             f.get('special_procedure_request'), f.get('date_sent') or None,
             f.get('urgency', 'Routine'), f.get('request_purpose', 'Judicial'),
             f.get('date_accepted') or None, f.get('accepted_by_name'), f.get('receiving_refno')),
            returning=True
        )
        req_id = new['lab_request_id']

        organ_names = request.form.getlist('organ_name[]')
        tissue_counts = request.form.getlist('no_of_tissue[]')
        for name, count in zip(organ_names, tissue_counts):
            if name.strip():
                database.execute(
                    "INSERT INTO lab_request_organ_tissue (lab_request_id, organ_name, no_of_tissue) VALUES (%s,%s,%s)",
                    (req_id, name, count or None)
                )

        database.execute("UPDATE case_master SET status='Awaiting Lab' WHERE case_id = "
                          "(SELECT ce.case_id FROM specimen sp JOIN case_event ce ON ce.event_id=sp.event_id WHERE sp.specimen_id=%s)",
                          (f['specimen_id'],))
        database.log_action(current_user.id, 'INSERT', 'lab_request', req_id, None, 'Lab request submitted')
        flash('Lab request submitted.', 'success')
        return redirect(url_for('lab.list_requests'))

    return render_template('lab/form.html', record=None, action='Add', specimens=specimens, staff=staff,
                           lab_names=LAB_NAMES, urgency_opts=URGENCY, purpose_opts=PURPOSE)


@lab_bp.route('/<int:rid>')
@login_required
@roles_required(*ALL_ROLES)
def view_request(rid):
    record = database.fetchone(
        """SELECT lr.*, sp.specimen_type, sp.specimen_label, cm.case_number, cm.case_id,
                  s.full_name AS requested_by_name
           FROM lab_request lr
           JOIN specimen sp ON sp.specimen_id = lr.specimen_id
           JOIN case_event ce ON ce.event_id = sp.event_id
           JOIN case_master cm ON cm.case_id = ce.case_id
           JOIN staff s ON s.staff_id = lr.requested_by_staff_id
           WHERE lr.lab_request_id=%s""", (rid,)
    )
    if not record:
        flash('Lab request not found.', 'danger')
        return redirect(url_for('lab.list_requests'))

    organ_tissue = database.fetchall("SELECT * FROM lab_request_organ_tissue WHERE lab_request_id=%s", (rid,))
    result = database.fetchone("SELECT * FROM lab_result WHERE lab_request_id=%s", (rid,))
    return render_template('lab/view.html', record=record, organ_tissue=organ_tissue, result=result)


@lab_bp.route('/<int:rid>/result', methods=['GET', 'POST'])
@login_required
@roles_required(*LAB_ROLES)
def add_result(rid):
    lab_request = database.fetchone("SELECT * FROM lab_request WHERE lab_request_id=%s", (rid,))
    if not lab_request:
        flash('Lab request not found.', 'danger')
        return redirect(url_for('lab.list_requests'))

    if request.method == 'POST':
        f = request.form
        existing = database.fetchone("SELECT lab_result_id FROM lab_result WHERE lab_request_id=%s", (rid,))
        if existing:
            database.execute(
                """UPDATE lab_result SET laboratory_no=%s, result_date=%s, received_by=%s,
                   lab_notes=%s, findings=%s, reported_by=%s, checked_by=%s, sent_on_date=%s
                   WHERE lab_request_id=%s""",
                (f.get('laboratory_no'), f.get('result_date') or None, f.get('received_by'),
                 f.get('lab_notes'), f.get('findings'), f.get('reported_by'), f.get('checked_by'),
                 f.get('sent_on_date') or None, rid)
            )
        else:
            database.execute(
                """INSERT INTO lab_result (lab_request_id, laboratory_no, result_date, received_by,
                   lab_notes, findings, reported_by, checked_by, sent_on_date)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (rid, f.get('laboratory_no'), f.get('result_date') or None, f.get('received_by'),
                 f.get('lab_notes'), f.get('findings'), f.get('reported_by'), f.get('checked_by'),
                 f.get('sent_on_date') or None)
            )
        database.log_action(current_user.id, 'INSERT', 'lab_result', rid, None, 'Lab result entered')
        flash('Lab result saved.', 'success')
        return redirect(url_for('lab.view_request', rid=rid))

    result = database.fetchone("SELECT * FROM lab_result WHERE lab_request_id=%s", (rid,))
    return render_template('lab/result_form.html', lab_request=lab_request, result=result)


@lab_bp.route('/<int:rid>/delete', methods=['POST'])
@login_required
@roles_required(*LAB_ROLES)
def delete_request(rid):
    database.execute("DELETE FROM lab_request WHERE lab_request_id=%s", (rid,))
    database.log_action(current_user.id, 'DELETE', 'lab_request', rid, None, 'Lab request deleted')
    flash('Lab request deleted.', 'warning')
    return redirect(url_for('lab.list_requests'))
