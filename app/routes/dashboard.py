from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import database

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def home():
    # Stats cards
    total_cases    = database.fetchone("SELECT COUNT(*) AS n FROM forensic_case")['n']
    open_cases     = database.fetchone("SELECT COUNT(*) AS n FROM forensic_case WHERE status='Open'")['n']
    inprog_cases   = database.fetchone("SELECT COUNT(*) AS n FROM forensic_case WHERE status='In Progress'")['n']
    closed_cases   = database.fetchone("SELECT COUNT(*) AS n FROM forensic_case WHERE status='Closed'")['n']
    total_patients = database.fetchone("SELECT COUNT(*) AS n FROM patient")['n']
    pending_labs   = database.fetchone("SELECT COUNT(*) AS n FROM lab_test WHERE status='Pending'")['n']
    pending_reports= database.fetchone("SELECT COUNT(*) AS n FROM court_report WHERE status='Draft'")['n']

    # Chart: cases by type
    by_type = database.fetchall(
        "SELECT case_type, COUNT(*) AS total FROM forensic_case GROUP BY case_type ORDER BY total DESC"
    )

    # Chart: cases by month (last 6 months)
    by_month = database.fetchall(
        """SELECT TO_CHAR(admission_date, 'Mon YYYY') AS month,
                  COUNT(*) AS total
           FROM forensic_case
           WHERE admission_date >= NOW() - INTERVAL '6 months'
           GROUP BY month, DATE_TRUNC('month', admission_date)
           ORDER BY DATE_TRUNC('month', admission_date)"""
    )

    # Recent cases
    recent = database.fetchall(
        """SELECT fc.case_id, fc.case_number, fc.case_type, fc.status,
                  fc.admission_date, p.full_name AS patient_name
           FROM forensic_case fc
           LEFT JOIN patient p ON p.patient_id = fc.patient_id
           ORDER BY fc.created_at DESC LIMIT 5"""
    )

    return render_template('dashboard.html',
        total_cases=total_cases, open_cases=open_cases,
        inprog_cases=inprog_cases, closed_cases=closed_cases,
        total_patients=total_patients, pending_labs=pending_labs,
        pending_reports=pending_reports,
        by_type=by_type, by_month=by_month, recent=recent
    )