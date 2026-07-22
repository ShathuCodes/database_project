import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from app.helpers import roles_required, ALL_ROLES, CLINICAL
from app import database

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

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


def _get_report_full_details(rid):
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
        return None, None, None, None, None, [], []

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

    return report, event, clinical, postmortem, skeletal, injuries, organs


@reports_bp.route('/<int:rid>/view')
@login_required
@roles_required(*ALL_ROLES)
def view_report(rid):
    report, event, clinical, postmortem, skeletal, injuries, organs = _get_report_full_details(rid)
    if not report:
        flash('Report not found.', 'danger')
        return redirect(url_for('reports.list_reports'))

    return render_template('reports/view.html', report=report, event=event, clinical=clinical,
                           postmortem=postmortem, skeletal=skeletal, injuries=injuries, organs=organs)


@reports_bp.route('/<int:rid>/download-pdf')
@login_required
@roles_required(*ALL_ROLES)
def download_pdf(rid):
    report, event, clinical, postmortem, skeletal, injuries, organs = _get_report_full_details(rid)
    if not report:
        flash('Report not found.', 'danger')
        return redirect(url_for('reports.list_reports'))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        alignment=1,
        textColor=colors.HexColor('#1e293b')
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor('#475569')
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=6
    )
    cell_text = ParagraphStyle('CellText', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12)
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12)

    # Header Section
    story.append(Paragraph("DEPARTMENT OF FORENSIC MEDICINE & MEDICO-LEGAL SERVICES", title_style))
    story.append(Spacer(1, 4))
    station_txt = report['staff_station'] or 'Judicial Medical Officer Office'
    story.append(Paragraph(f"{station_txt} — Official Judicial Report", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"OFFICIAL {report['report_type']} (MEDICO-LEGAL REPORT)", ParagraphStyle('RepHeader', parent=title_style, fontSize=12, textColor=colors.HexColor('#1d4ed8'))))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    # Case & Metadata Table
    meta_data = [
        [Paragraph("Case Number:", cell_bold), Paragraph(str(report['case_number']), cell_text), Paragraph("Court:", cell_bold), Paragraph(str(report['court_name'] or 'N/A'), cell_text)],
        [Paragraph("Serial No:", cell_bold), Paragraph(str(report['serial_no'] or 'N/A'), cell_text), Paragraph("Magistrate:", cell_bold), Paragraph(str(report['magistrate_name'] or 'N/A'), cell_text)],
        [Paragraph("Case Type:", cell_bold), Paragraph(str(report['case_type']), cell_text), Paragraph("Date Issued:", cell_bold), Paragraph(str(report['date_issued'].strftime('%Y-%m-%d %H:%M') if report['date_issued'] else 'N/A'), cell_text)],
        [Paragraph("Police Station:", cell_bold), Paragraph(str(report['police_station'] or 'N/A'), cell_text), Paragraph("Report Status:", cell_bold), Paragraph(str(report['status']), cell_text)]
    ]
    t_meta = Table(meta_data, colWidths=[100, 160, 100, 160])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # Patient Details Table
    story.append(Paragraph("Patient / Subject Information", section_heading))
    patient_data = [
        [Paragraph("Full Name:", cell_bold), Paragraph(str(report['patient_name'] or 'Unidentified'), cell_text), Paragraph("NIC/Passport:", cell_bold), Paragraph(str(report['patient_nic'] or 'N/A'), cell_text)],
        [Paragraph("Gender / Age:", cell_bold), Paragraph(f"{report['patient_gender'] or 'N/A'} / {report['patient_age'] or 'N/A'} yrs", cell_text), Paragraph("Occupation:", cell_bold), Paragraph(str(report['patient_occupation'] or 'N/A'), cell_text)],
        [Paragraph("Address:", cell_bold), Paragraph(str(report['patient_address'] or 'N/A'), cell_text), Paragraph("", cell_text), Paragraph("", cell_text)]
    ]
    t_patient = Table(patient_data, colWidths=[100, 160, 100, 160])
    t_patient.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('SPAN', (1,2), (3,2))
    ]))
    story.append(t_patient)
    story.append(Spacer(1, 12))

    # Postmortem / Clinical Examination Findings
    if postmortem:
        story.append(Paragraph("Postmortem Examination Findings", section_heading))
        pm_data = [
            [Paragraph("Time of Death:", cell_bold), Paragraph(str(postmortem['date_time_of_death'] or 'N/A'), cell_text)],
            [Paragraph("Place of Exam:", cell_bold), Paragraph(str(postmortem['place_of_examination'] or 'N/A'), cell_text)],
            [Paragraph("Scene Info:", cell_bold), Paragraph(str(postmortem['scene_description'] or 'N/A'), cell_text)],
            [Paragraph("External Findings:", cell_bold), Paragraph(str(postmortem['external_exam_description'] or 'N/A'), cell_text)],
            [Paragraph("Cause of Death:", cell_bold), Paragraph(str(postmortem['cause_of_death'] or 'Pending Analysis'), ParagraphStyle('COD', parent=cell_bold, textColor=colors.HexColor('#dc2626')))],
            [Paragraph("Medical Conclusion:", cell_bold), Paragraph(str(postmortem['conclusion'] or 'N/A'), cell_text)]
        ]
        t_pm = Table(pm_data, colWidths=[130, 390])
        t_pm.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_pm)
        story.append(Spacer(1, 12))

    if clinical:
        story.append(Paragraph("Clinical Examination Findings", section_heading))
        clin_data = [
            [Paragraph("History Given:", cell_bold), Paragraph(str(clinical['history_given'] or 'N/A'), cell_text)],
            [Paragraph("Place of Exam:", cell_bold), Paragraph(str(clinical['place_of_exam'] or 'N/A'), cell_text)],
            [Paragraph("Alcohol / Drugs:", cell_bold), Paragraph(f"Alcohol: {clinical['under_influence_alcohol'] or 'No'} | Drugs: {clinical['under_influence_drugs'] or 'No'}", cell_text)],
            [Paragraph("Medical Opinion:", cell_bold), Paragraph(str(clinical['other_opinions'] or 'N/A'), cell_text)]
        ]
        t_clin = Table(clin_data, colWidths=[130, 390])
        t_clin.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_clin)
        story.append(Spacer(1, 12))

    # Injuries Table
    if injuries:
        story.append(Paragraph("Recorded Injuries & Penal Code Classification", section_heading))
        inj_rows = [[Paragraph("#", cell_bold), Paragraph("Nature of Injury", cell_bold), Paragraph("Site", cell_bold), Paragraph("Weapon", cell_bold), Paragraph("Category", cell_bold), Paragraph("Grievous Clause", cell_bold)]]
        for idx, inj in enumerate(injuries, 1):
            inj_rows.append([
                Paragraph(str(idx), cell_text),
                Paragraph(f"<b>{inj['nature']}</b><br/>{inj['size_shape'] or ''}", cell_text),
                Paragraph(str(inj['site']), cell_text),
                Paragraph(str(inj['causative_weapon']), cell_text),
                Paragraph(str(inj['category_of_hurt']), cell_text),
                Paragraph(str(inj['grievous_clause_desc'] or inj['grievous_hurt_clause_code'] or 'N/A'), cell_text)
            ])
        t_inj = Table(inj_rows, colWidths=[20, 130, 100, 90, 80, 100])
        t_inj.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fee2e2')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#fca5a5')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#fecaca')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_inj)
        story.append(Spacer(1, 15))

    # Signature Block Table
    sig_data = [
        [
            Paragraph("<b>OFFICIAL HOSPITAL / DEPT SEAL</b><br/><br/><br/>[ SEAL STAMP ]", ParagraphStyle('Seal', parent=cell_text, alignment=1)),
            Paragraph(f"<b>Prepared By:</b> {report['prepared_by_name']}<br/><b>Designation:</b> {report['staff_designation'] or 'Judicial Medical Officer'}<br/><b>SLMC Reg No:</b> {report['slmc_regno'] or 'N/A'}<br/><b>Date:</b> {report['date_issued'].strftime('%Y-%m-%d') if report['date_issued'] else 'N/A'}<br/><br/>_______________________________<br/>Doctor Signature", cell_text)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[250, 270])
    t_sig.setStyle(TableStyle([
        ('BOX', (0,0), (0,0), 1, colors.HexColor('#94a3b8')),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f8fafc')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_sig)

    doc.build(story)
    buffer.seek(0)
    pdf_data = buffer.getvalue()

    filename = f"Report_{report['case_number'].replace('/', '_')}_{report['report_type']}.pdf"
    return Response(
        pdf_data,
        mimetype="application/pdf",
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
