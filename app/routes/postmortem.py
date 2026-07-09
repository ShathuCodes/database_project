from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required, CLINICAL, ALL_ROLES
from app import database

postmortem_bp = Blueprint('postmortem', __name__)

SEX_OPTIONS = ['M', 'F', 'Unknown']


@postmortem_bp.route('/')
@login_required
@roles_required(*ALL_ROLES)
def list_pm():
    search = request.args.get('search', '').strip()

    sql = """SELECT pm.event_id, pm.cause_of_death, pm.conclusion, pm.district,
                    ce.event_date, ce.case_id, cm.case_number, s.full_name AS staff_name
             FROM postmortem pm
             JOIN case_event ce ON ce.event_id = pm.event_id
             JOIN case_master cm ON cm.case_id = ce.case_id
             JOIN staff s ON s.staff_id = ce.staff_id
             WHERE 1=1"""
    params = []
    if search:
        sql += " AND (cm.case_number ILIKE %s OR pm.cause_of_death ILIKE %s)"
        params.extend([f'%{search}%'] * 2)
    sql += " ORDER BY ce.event_date DESC"
    records = database.fetchall(sql, params)
    return render_template('postmortem/list.html', records=records, search=search)


@postmortem_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required(*CLINICAL)
def add_pm():
    cases = database.fetchall(
        "SELECT case_id, case_number FROM case_master WHERE status <> 'Despatched' ORDER BY case_id DESC")
    staff = database.fetchall("SELECT staff_id, full_name FROM staff ORDER BY full_name")

    if request.method == 'POST':
        f = request.form

        def _txn(cur):
            cur.execute(
                "INSERT INTO case_event (case_id, event_type, event_date, staff_id) VALUES (%s,'Postmortem',%s,%s) RETURNING event_id",
                (f['case_id'], f['event_date'], f['staff_id'])
            )
            event_id = cur.fetchone()['event_id']
            cur.execute(
                """INSERT INTO postmortem
                   (event_id, date_time_of_death, requested_by_name, requested_by_designation,
                    district, place_of_examination, scene_description, external_exam_description,
                    estimated_age, sex, height_cm, eyes_and_pupils, hair_description,
                    teeth_condition, tongue_condition, primary_flaccidity, rigor_mortis,
                    hypostasis, putrefaction, hands_nails_condition, cause_of_death,
                    time_since_death, register_serial_no, conclusion)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (event_id, f.get('date_time_of_death') or None, f.get('requested_by_name'),
                 f.get('requested_by_designation'), f.get('district'), f.get('place_of_examination'),
                 f.get('scene_description'), f.get('external_exam_description'),
                 f.get('estimated_age'), f.get('sex') or None, f.get('height_cm') or None,
                 f.get('eyes_and_pupils'), f.get('hair_description'), f.get('teeth_condition'),
                 f.get('tongue_condition'), f.get('primary_flaccidity'), f.get('rigor_mortis'),
                 f.get('hypostasis'), f.get('putrefaction'), f.get('hands_nails_condition'),
                 f.get('cause_of_death'), f.get('time_since_death'), f.get('register_serial_no'),
                 f.get('conclusion'))
            )
            cur.execute("UPDATE case_master SET status='Report Pending' WHERE case_id=%s", (f['case_id'],))
            return event_id

        event_id = database.run_in_transaction(_txn)
        database.log_action(current_user.id, 'INSERT', 'postmortem', event_id, None, 'Postmortem recorded')
        flash('Postmortem record added.', 'success')
        return redirect(url_for('postmortem.view_pm', eid=event_id))

    return render_template('postmortem/form.html', record=None, event=None, action='Add',
                           cases=cases, staff=staff, sex_options=SEX_OPTIONS)


@postmortem_bp.route('/<int:eid>')
@login_required
@roles_required(*ALL_ROLES)
def view_pm(eid):
    record = database.fetchone(
        """SELECT pm.*, ce.case_id, ce.event_date, ce.staff_id, cm.case_number, s.full_name AS staff_name
           FROM postmortem pm
           JOIN case_event ce ON ce.event_id = pm.event_id
           JOIN case_master cm ON cm.case_id = ce.case_id
           JOIN staff s ON s.staff_id = ce.staff_id
           WHERE pm.event_id=%s""", (eid,)
    )
    if not record:
        flash('Postmortem record not found.', 'danger')
        return redirect(url_for('postmortem.list_pm'))

    organ_findings = database.fetchall(
        "SELECT * FROM postmortem_organ_finding WHERE event_id=%s ORDER BY organ_finding_id", (eid,))
    identifiers = database.fetchall(
        "SELECT * FROM body_identifier WHERE event_id=%s ORDER BY identifier_id", (eid,))
    injuries = database.fetchall(
        """SELECT i.*, g.description AS clause_description FROM injury i
           LEFT JOIN grievous_hurt_type g ON g.clause_code = i.grievous_hurt_clause_code
           WHERE i.event_id=%s ORDER BY i.injury_id""", (eid,))
    specimens = database.fetchall("SELECT * FROM specimen WHERE event_id=%s ORDER BY specimen_id", (eid,))
    clause_types = database.fetchall("SELECT * FROM grievous_hurt_type ORDER BY clause_code")

    return render_template('postmortem/view.html', record=record,
                           organ_findings=organ_findings, identifiers=identifiers,
                           injuries=injuries, specimens=specimens, clause_types=clause_types)


@postmortem_bp.route('/<int:eid>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(*CLINICAL)
def edit_pm(eid):
    record = database.fetchone(
        """SELECT pm.*, ce.case_id, ce.event_date, ce.staff_id FROM postmortem pm
           JOIN case_event ce ON ce.event_id = pm.event_id WHERE pm.event_id=%s""", (eid,))
    if not record:
        flash('Postmortem record not found.', 'danger')
        return redirect(url_for('postmortem.list_pm'))

    cases = database.fetchall("SELECT case_id, case_number FROM case_master ORDER BY case_id DESC")
    staff = database.fetchall("SELECT staff_id, full_name FROM staff ORDER BY full_name")

    if request.method == 'POST':
        f = request.form
        database.execute(
            "UPDATE case_event SET event_date=%s, staff_id=%s WHERE event_id=%s",
            (f['event_date'], f['staff_id'], eid)
        )
        database.execute(
            """UPDATE postmortem SET date_time_of_death=%s, requested_by_name=%s,
               requested_by_designation=%s, district=%s, place_of_examination=%s,
               scene_description=%s, external_exam_description=%s, estimated_age=%s,
               sex=%s, height_cm=%s, eyes_and_pupils=%s, hair_description=%s,
               teeth_condition=%s, tongue_condition=%s, primary_flaccidity=%s,
               rigor_mortis=%s, hypostasis=%s, putrefaction=%s, hands_nails_condition=%s,
               cause_of_death=%s, time_since_death=%s, register_serial_no=%s, conclusion=%s
               WHERE event_id=%s""",
            (f.get('date_time_of_death') or None, f.get('requested_by_name'),
             f.get('requested_by_designation'), f.get('district'), f.get('place_of_examination'),
             f.get('scene_description'), f.get('external_exam_description'),
             f.get('estimated_age'), f.get('sex') or None, f.get('height_cm') or None,
             f.get('eyes_and_pupils'), f.get('hair_description'), f.get('teeth_condition'),
             f.get('tongue_condition'), f.get('primary_flaccidity'), f.get('rigor_mortis'),
             f.get('hypostasis'), f.get('putrefaction'), f.get('hands_nails_condition'),
             f.get('cause_of_death'), f.get('time_since_death'), f.get('register_serial_no'),
             f.get('conclusion'), eid)
        )
        database.log_action(current_user.id, 'UPDATE', 'postmortem', eid, None, 'Postmortem updated')
        flash('Postmortem record updated.', 'success')
        return redirect(url_for('postmortem.view_pm', eid=eid))

    return render_template('postmortem/form.html', record=record, event=record, action='Edit',
                           cases=cases, staff=staff, sex_options=SEX_OPTIONS)


@postmortem_bp.route('/<int:eid>/delete', methods=['POST'])
@login_required
@roles_required(*CLINICAL)
def delete_pm(eid):
    database.execute("DELETE FROM case_event WHERE event_id=%s", (eid,))  # cascades to postmortem
    database.log_action(current_user.id, 'DELETE', 'postmortem', eid, None, 'Postmortem deleted')
    flash('Record deleted.', 'warning')
    return redirect(url_for('postmortem.list_pm'))


# ---- Organ findings, body identifiers, injuries (inline sub-forms) ----

@postmortem_bp.route('/<int:eid>/organ-finding', methods=['POST'])
@login_required
@roles_required(*CLINICAL)
def add_organ_finding(eid):
    f = request.form
    database.execute(
        "INSERT INTO postmortem_organ_finding (event_id, organ_name, findings) VALUES (%s,%s,%s)",
        (eid, f['organ_name'], f.get('findings'))
    )
    flash('Organ finding added.', 'success')
    return redirect(url_for('postmortem.view_pm', eid=eid))


@postmortem_bp.route('/<int:eid>/identifier', methods=['POST'])
@login_required
@roles_required(*CLINICAL)
def add_identifier(eid):
    f = request.form
    database.execute(
        "INSERT INTO body_identifier (event_id, name, address, relationship_to_deceased) VALUES (%s,%s,%s,%s)",
        (eid, f['name'], f.get('address'), f.get('relationship_to_deceased'))
    )
    flash('Body identifier added.', 'success')
    return redirect(url_for('postmortem.view_pm', eid=eid))


@postmortem_bp.route('/<int:eid>/injury', methods=['POST'])
@login_required
@roles_required(*CLINICAL)
def add_injury(eid):
    f = request.form
    database.execute(
        """INSERT INTO injury (event_id, nature, size_shape, site, causative_weapon,
           body_cavity, category_of_hurt, endangers_life, timing_relative_to_death,
           grievous_hurt_clause_code, explanatory_remarks)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (eid, f.get('nature'), f.get('size_shape'), f.get('site'), f.get('causative_weapon'),
         f.get('body_cavity') or None, f.get('category_of_hurt') or None,
         'endangers_life' in f, f.get('timing_relative_to_death') or None,
         f.get('grievous_hurt_clause_code') or None, f.get('explanatory_remarks'))
    )
    flash('Injury recorded.', 'success')
    return redirect(url_for('postmortem.view_pm', eid=eid))
