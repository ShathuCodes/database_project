from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.helpers import roles_required, CLINICAL, ALL_ROLES
from app import database

clinical_bp = Blueprint('clinical', __name__)

YES_NO_UNCERTAIN = ['Yes', 'No', 'Uncertain']
YES_NO_NOTTESTED = ['Yes', 'No', 'Not tested']


@clinical_bp.route('/')
@login_required
@roles_required(*ALL_ROLES)
def list_clinical():
    search = request.args.get('search', '').strip()
    sql = """SELECT ce_.event_id, ce_.reason_for_referral, ce.event_date, ce.case_id,
                    cm.case_number, s.full_name AS staff_name
             FROM clinical_examination ce_
             JOIN case_event ce ON ce.event_id = ce_.event_id
             JOIN case_master cm ON cm.case_id = ce.case_id
             JOIN staff s ON s.staff_id = ce.staff_id
             WHERE 1=1"""
    params = []
    if search:
        sql += " AND (cm.case_number ILIKE %s OR ce_.reason_for_referral ILIKE %s)"
        params.extend([f'%{search}%'] * 2)
    sql += " ORDER BY ce.event_date DESC"
    records = database.fetchall(sql, params)
    return render_template('clinical/list.html', records=records, search=search)


@clinical_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required(*CLINICAL)
def add_clinical():
    cases = database.fetchall(
        "SELECT case_id, case_number FROM case_master WHERE status <> 'Despatched' ORDER BY case_id DESC")
    staff = database.fetchall("SELECT staff_id, full_name FROM staff ORDER BY full_name")

    if request.method == 'POST':
        f = request.form

        def _txn(cur):
            cur.execute(
                "INSERT INTO case_event (case_id, event_type, event_date, staff_id) VALUES (%s,'Clinical Examination',%s,%s) RETURNING event_id",
                (f['case_id'], f['event_date'], f['staff_id'])
            )
            event_id = cur.fetchone()['event_id']
            cur.execute(
                """INSERT INTO clinical_examination
                   (event_id, history_given, place_of_exam, hospital_no, ward, bed_no,
                    admission_date, discharge_date, consent_obtained, reason_for_referral,
                    alcohol_smell_present, under_influence_alcohol, drugs_consumed,
                    under_influence_drugs, investigations_ordered, referrals_made, other_opinions)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (event_id, f.get('history_given'), f.get('place_of_exam'), f.get('hospital_no'),
                 f.get('ward'), f.get('bed_no'), f.get('admission_date') or None,
                 f.get('discharge_date') or None, 'consent_obtained' in f,
                 f.get('reason_for_referral'), 'alcohol_smell_present' in f,
                 f.get('under_influence_alcohol') or None, f.get('drugs_consumed') or None,
                 f.get('under_influence_drugs') or None, f.get('investigations_ordered'),
                 f.get('referrals_made'), f.get('other_opinions'))
            )
            if f.get('is_sexual_assault') == 'on':
                cur.execute(
                    """INSERT INTO sexual_assault_finding
                       (event_id, history_of_assault_given, vaginal_hymen_signs_present,
                        anal_penetration_signs_present, inter_labial_penetration_signs_present, remarks)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (event_id, f.get('history_of_assault_given'),
                     'vaginal_hymen_signs_present' in f, 'anal_penetration_signs_present' in f,
                     'inter_labial_penetration_signs_present' in f, f.get('saf_remarks'))
                )
            return event_id

        event_id = database.run_in_transaction(_txn)
        database.log_action(current_user.id, 'INSERT', 'clinical_examination', event_id, None, 'Clinical examination recorded')
        flash('Clinical examination recorded.', 'success')
        return redirect(url_for('clinical.view_clinical', eid=event_id))

    return render_template('clinical/form.html', record=None, action='Add', cases=cases, staff=staff,
                           yn_uncertain=YES_NO_UNCERTAIN, yn_nottested=YES_NO_NOTTESTED)


@clinical_bp.route('/<int:eid>')
@login_required
@roles_required(*ALL_ROLES)
def view_clinical(eid):
    record = database.fetchone(
        """SELECT c.*, ce.case_id, ce.event_date, cm.case_number, s.full_name AS staff_name
           FROM clinical_examination c
           JOIN case_event ce ON ce.event_id = c.event_id
           JOIN case_master cm ON cm.case_id = ce.case_id
           JOIN staff s ON s.staff_id = ce.staff_id
           WHERE c.event_id=%s""", (eid,)
    )
    if not record:
        flash('Clinical examination not found.', 'danger')
        return redirect(url_for('clinical.list_clinical'))

    saf = database.fetchone("SELECT * FROM sexual_assault_finding WHERE event_id=%s", (eid,))
    injuries = database.fetchall(
        """SELECT i.*, g.description AS clause_description FROM injury i
           LEFT JOIN grievous_hurt_type g ON g.clause_code = i.grievous_hurt_clause_code
           WHERE i.event_id=%s ORDER BY i.injury_id""", (eid,))
    specimens = database.fetchall("SELECT * FROM specimen WHERE event_id=%s ORDER BY specimen_id", (eid,))
    clause_types = database.fetchall("SELECT * FROM grievous_hurt_type ORDER BY clause_code")

    return render_template('clinical/view.html', record=record, saf=saf, injuries=injuries,
                           specimens=specimens, clause_types=clause_types)


@clinical_bp.route('/<int:eid>/injury', methods=['POST'])
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
    return redirect(url_for('clinical.view_clinical', eid=eid))


@clinical_bp.route('/<int:eid>/delete', methods=['POST'])
@login_required
@roles_required(*CLINICAL)
def delete_clinical(eid):
    database.execute("DELETE FROM case_event WHERE event_id=%s", (eid,))
    database.log_action(current_user.id, 'DELETE', 'clinical_examination', eid, None, 'Clinical examination deleted')
    flash('Record deleted.', 'warning')
    return redirect(url_for('clinical.list_clinical'))
