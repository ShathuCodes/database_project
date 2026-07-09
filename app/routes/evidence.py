from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required, ALL_ROLES, CLINICAL
from app import database

evidence_bp = Blueprint('evidence', __name__)


@evidence_bp.route('/')
@login_required
@roles_required(*ALL_ROLES)
def list_evidence():
    search  = request.args.get('search', '').strip()
    case_id = request.args.get('case_id', '')

    sql = """SELECT sp.*, ce.event_type, ce.case_id, cm.case_number
             FROM specimen sp
             JOIN case_event ce ON ce.event_id = sp.event_id
             JOIN case_master cm ON cm.case_id = ce.case_id
             WHERE 1=1"""
    params = []
    if search:
        sql += " AND (sp.specimen_type ILIKE %s OR sp.specimen_label ILIKE %s OR cm.case_number ILIKE %s)"
        params.extend([f'%{search}%'] * 3)
    if case_id:
        sql += " AND ce.case_id = %s"
        params.append(case_id)
    sql += " ORDER BY sp.collection_date DESC"
    records = database.fetchall(sql, params)
    cases = database.fetchall("SELECT case_id, case_number FROM case_master ORDER BY case_id DESC")
    return render_template('evidence/list.html', records=records, cases=cases,
                           search=search, case_id=case_id)


@evidence_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required(*CLINICAL)
def add_evidence():
    events = database.fetchall(
        """SELECT ce.event_id, ce.event_type, cm.case_number
           FROM case_event ce JOIN case_master cm ON cm.case_id = ce.case_id
           ORDER BY ce.event_id DESC""")
    if request.method == 'POST':
        f = request.form
        new = database.execute(
            """INSERT INTO specimen (event_id, specimen_type, specimen_label, collection_date,
               seal_no, chain_of_custody_status, production_number)
               VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING specimen_id""",
            (f['event_id'], f['specimen_type'], f.get('specimen_label'),
             f.get('collection_date') or None, f.get('seal_no'),
             f.get('chain_of_custody_status', 'Collected'), f.get('production_number')),
            returning=True
        )
        database.log_action(current_user.id, 'INSERT', 'specimen', new['specimen_id'], None, 'Specimen collected')
        flash('Specimen recorded.', 'success')
        return redirect(url_for('evidence.list_evidence'))
    return render_template('evidence/form.html', record=None, action='Add', events=events)


@evidence_bp.route('/<int:sid>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(*CLINICAL)
def edit_evidence(sid):
    record = database.fetchone("SELECT * FROM specimen WHERE specimen_id=%s", (sid,))
    if not record:
        flash('Specimen not found.', 'danger')
        return redirect(url_for('evidence.list_evidence'))
    events = database.fetchall(
        """SELECT ce.event_id, ce.event_type, cm.case_number
           FROM case_event ce JOIN case_master cm ON cm.case_id = ce.case_id
           ORDER BY ce.event_id DESC""")
    if request.method == 'POST':
        f = request.form
        database.execute(
            """UPDATE specimen SET event_id=%s, specimen_type=%s, specimen_label=%s,
               collection_date=%s, seal_no=%s, chain_of_custody_status=%s, production_number=%s
               WHERE specimen_id=%s""",
            (f['event_id'], f['specimen_type'], f.get('specimen_label'),
             f.get('collection_date') or None, f.get('seal_no'),
             f.get('chain_of_custody_status'), f.get('production_number'), sid)
        )
        database.log_action(current_user.id, 'UPDATE', 'specimen', sid, None, 'Specimen updated')
        flash('Specimen updated.', 'success')
        return redirect(url_for('evidence.list_evidence'))
    return render_template('evidence/form.html', record=record, action='Edit', events=events)


@evidence_bp.route('/<int:sid>/delete', methods=['POST'])
@login_required
@roles_required(*CLINICAL)
def delete_evidence(sid):
    database.execute("DELETE FROM specimen WHERE specimen_id=%s", (sid,))
    database.log_action(current_user.id, 'DELETE', 'specimen', sid, None, 'Specimen deleted')
    flash('Specimen deleted.', 'warning')
    return redirect(url_for('evidence.list_evidence'))
