from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required, CLINICAL, ALL_ROLES
from app import database

skeletal_bp = Blueprint('skeletal', __name__)

SEAL_STATUSES = ['Intact', 'Broken', 'No Seal']
ITEM_CATEGORIES = ['Human Remain', 'Other Content']


@skeletal_bp.route('/')
@login_required
@roles_required(*ALL_ROLES)
def list_skeletal():
    search = request.args.get('search', '').strip()
    sql = """SELECT sk.event_id, sk.specimen_no, sk.gender_conclusion, sk.age_conclusion,
                    ce.event_date, ce.case_id, cm.case_number, s.full_name AS staff_name
             FROM skeletal_examination sk
             JOIN case_event ce ON ce.event_id = sk.event_id
             JOIN case_master cm ON cm.case_id = ce.case_id
             JOIN staff s ON s.staff_id = ce.staff_id
             WHERE 1=1"""
    params = []
    if search:
        sql += " AND (cm.case_number ILIKE %s OR sk.specimen_no ILIKE %s)"
        params.extend([f'%{search}%'] * 2)
    sql += " ORDER BY ce.event_date DESC"
    records = database.fetchall(sql, params)
    return render_template('skeletal/list.html', records=records, search=search)


@skeletal_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required(*CLINICAL)
def add_skeletal():
    cases = database.fetchall(
        "SELECT case_id, case_number FROM case_master WHERE status <> 'Despatched' ORDER BY case_id DESC")
    staff = database.fetchall("SELECT staff_id, full_name FROM staff ORDER BY full_name")

    if request.method == 'POST':
        f = request.form

        def _txn(cur):
            cur.execute(
                "INSERT INTO case_event (case_id, event_type, event_date, staff_id) VALUES (%s,'Skeletal Examination',%s,%s) RETURNING event_id",
                (f['case_id'], f['event_date'], f['staff_id'])
            )
            event_id = cur.fetchone()['event_id']
            cur.execute(
                """INSERT INTO skeletal_examination
                   (event_id, history, specimen_no, place_found, seal_status, wrapping_description,
                    human_remains_present, animal_remains_present, state_of_putrefaction,
                    skeletonized, mummified, min_no_individuals, mni_reasons, gender_conclusion,
                    age_conclusion, stature_estimate, stature_method, time_since_death,
                    cause_of_death_opinion, special_techniques_recommended, supervised_by_staff_id)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (event_id, f.get('history'), f.get('specimen_no') or None, f.get('place_found'),
                 f.get('seal_status') or None, f.get('wrapping_description'),
                 'human_remains_present' in f, 'animal_remains_present' in f,
                 f.get('state_of_putrefaction'), 'skeletonized' in f, 'mummified' in f,
                 f.get('min_no_individuals') or None, f.get('mni_reasons'),
                 f.get('gender_conclusion'), f.get('age_conclusion'), f.get('stature_estimate'),
                 f.get('stature_method'), f.get('time_since_death'), f.get('cause_of_death_opinion'),
                 f.get('special_techniques_recommended'), f.get('supervised_by_staff_id') or None)
            )
            return event_id

        event_id = database.run_in_transaction(_txn)
        database.log_action(current_user.id, 'INSERT', 'skeletal_examination', event_id, None, 'Skeletal examination recorded')
        flash('Skeletal examination recorded.', 'success')
        return redirect(url_for('skeletal.view_skeletal', eid=event_id))

    return render_template('skeletal/form.html', record=None, action='Add', cases=cases, staff=staff,
                           seal_statuses=SEAL_STATUSES)


@skeletal_bp.route('/<int:eid>')
@login_required
@roles_required(*ALL_ROLES)
def view_skeletal(eid):
    record = database.fetchone(
        """SELECT sk.*, ce.case_id, ce.event_date, cm.case_number, s.full_name AS staff_name,
                  sup.full_name AS supervised_by_name
           FROM skeletal_examination sk
           JOIN case_event ce ON ce.event_id = sk.event_id
           JOIN case_master cm ON cm.case_id = ce.case_id
           JOIN staff s ON s.staff_id = ce.staff_id
           LEFT JOIN staff sup ON sup.staff_id = sk.supervised_by_staff_id
           WHERE sk.event_id=%s""", (eid,)
    )
    if not record:
        flash('Skeletal examination not found.', 'danger')
        return redirect(url_for('skeletal.list_skeletal'))

    items = database.fetchall("SELECT * FROM skeletal_item WHERE event_id=%s ORDER BY item_id", (eid,))
    specimens = database.fetchall("SELECT * FROM specimen WHERE event_id=%s ORDER BY specimen_id", (eid,))
    return render_template('skeletal/view.html', record=record, items=items, specimens=specimens,
                           item_categories=ITEM_CATEGORIES)


@skeletal_bp.route('/<int:eid>/item', methods=['POST'])
@login_required
@roles_required(*CLINICAL)
def add_item(eid):
    f = request.form
    database.execute(
        """INSERT INTO skeletal_item (event_id, item_category, description, serial_number, quantity)
           VALUES (%s,%s,%s,%s,%s)""",
        (eid, f['item_category'], f.get('description'), f.get('serial_number'), f.get('quantity') or 1)
    )
    flash('Item recorded.', 'success')
    return redirect(url_for('skeletal.view_skeletal', eid=eid))


@skeletal_bp.route('/<int:eid>/delete', methods=['POST'])
@login_required
@roles_required(*CLINICAL)
def delete_skeletal(eid):
    database.execute("DELETE FROM case_event WHERE event_id=%s", (eid,))
    database.log_action(current_user.id, 'DELETE', 'skeletal_examination', eid, None, 'Skeletal examination deleted')
    flash('Record deleted.', 'warning')
    return redirect(url_for('skeletal.list_skeletal'))
