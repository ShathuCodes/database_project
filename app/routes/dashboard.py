from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import database

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def home():
    total_cases     = database.fetchone("SELECT COUNT(*) AS n FROM case_master")['n']
    under_exam      = database.fetchone("SELECT COUNT(*) AS n FROM case_master WHERE status='Under Examination'")['n']
    awaiting_lab    = database.fetchone("SELECT COUNT(*) AS n FROM case_master WHERE status='Awaiting Lab'")['n']
    report_pending  = database.fetchone("SELECT COUNT(*) AS n FROM case_master WHERE status='Report Pending'")['n']
    despatched      = database.fetchone("SELECT COUNT(*) AS n FROM case_master WHERE status='Despatched'")['n']
    total_patients  = database.fetchone("SELECT COUNT(*) AS n FROM patient")['n']
    pending_labs    = database.fetchone("SELECT COUNT(*) AS n FROM lab_request lr LEFT JOIN lab_result r ON r.lab_request_id=lr.lab_request_id WHERE r.lab_result_id IS NULL")['n']
    draft_reports   = database.fetchone("SELECT COUNT(*) AS n FROM report WHERE status='Draft'")['n']

    by_type = database.fetchall(
        "SELECT case_type, COUNT(*) AS total FROM case_master GROUP BY case_type ORDER BY total DESC"
    )

    by_month = database.fetchall(
        """SELECT TO_CHAR(received_date, 'Mon YYYY') AS month, COUNT(*) AS total
           FROM case_master
           WHERE received_date >= NOW() - INTERVAL '6 months'
           GROUP BY month, DATE_TRUNC('month', received_date)
           ORDER BY DATE_TRUNC('month', received_date)"""
    )

    recent = database.fetchall(
        """SELECT cm.case_id, cm.case_number, cm.case_type, cm.status,
                  cm.received_date, p.full_name AS patient_name
           FROM case_master cm
           LEFT JOIN patient p ON p.patient_id = cm.patient_id
           ORDER BY cm.created_at DESC LIMIT 5"""
    )

    notifications = []
    if current_user.is_authenticated:
        notifications = database.fetchall(
            """SELECT * FROM notification WHERE user_id=%s AND is_read = FALSE
               ORDER BY created_at DESC LIMIT 5""", (current_user.id,)
        )

    return render_template('dashboard.html',
        total_cases=total_cases, under_exam=under_exam, awaiting_lab=awaiting_lab,
        report_pending=report_pending, despatched=despatched,
        total_patients=total_patients, pending_labs=pending_labs,
        draft_reports=draft_reports,
        by_type=by_type, by_month=by_month, recent=recent,
        notifications=notifications
    )
