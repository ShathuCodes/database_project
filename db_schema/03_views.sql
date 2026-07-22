-- ============================================================
-- FORENSIC MEDICO-LEGAL DATABASE
-- 03_views.sql — System Database Views
-- ============================================================

-- ------------------------------------------------------------
-- View 1: Case Summary Overview
-- Combines Master Case Log with Patient, Police Station, and Court details.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_case_summary AS
SELECT
    cm.case_id,
    cm.case_number,
    cm.inquest_no,
    cm.case_type,
    cm.status,
    cm.incident_date,
    cm.received_date,
    cm.trial_date,
    p.patient_id,
    p.full_name      AS patient_name,
    p.nic_passportno AS patient_nic,
    p.gender         AS patient_gender,
    p.age            AS patient_age,
    ps.station_name  AS police_station,
    ps.division      AS police_division,
    c.court_name     AS court_name,
    m.name           AS magistrate_name
FROM case_master cm
LEFT JOIN patient p                  ON p.patient_id = cm.patient_id
LEFT JOIN police_station ps          ON ps.police_station_id = cm.police_station_id
LEFT JOIN court c                     ON c.court_id = cm.court_id
LEFT JOIN magistrate m                ON m.magistrate_id = cm.magistrate_id;

-- ------------------------------------------------------------
-- View 2: Case Statistics by Type and Status
-- Provides high-level dashboard metrics on case progress.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_stats_by_type AS
SELECT
    case_type,
    status,
    COUNT(*) AS total_cases
FROM case_master
GROUP BY case_type, status;

-- ------------------------------------------------------------
-- View 3: Pending Reports Tracking
-- Identifies reports that have not yet been despatched to court/police.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_pending_reports AS
SELECT
    r.report_id,
    r.serial_no       AS report_serial_no,
    r.report_type,
    r.status          AS report_status,
    r.date_issued,
    cm.case_id,
    cm.case_number,
    cm.case_type,
    cm.trial_date,
    s.full_name       AS prepared_by_staff
FROM report r
JOIN case_master cm ON cm.case_id = r.case_id
JOIN staff s       ON s.staff_id = r.prepared_by_staff_id
WHERE r.status <> 'Despatched';

-- ------------------------------------------------------------
-- View 4: Unified Case Event Overview
-- Unifies clinical, postmortem, and skeletal examination events into a single log.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_event_overview AS
SELECT
    ce.event_id,
    ce.case_id,
    cm.case_number,
    cm.case_type,
    ce.event_type,
    ce.event_date,
    s.staff_id,
    s.full_name AS conducted_by_staff,
    s.designation AS staff_designation
FROM case_event ce
JOIN case_master cm ON cm.case_id = ce.case_id
JOIN staff s       ON s.staff_id = ce.staff_id;

-- ------------------------------------------------------------
-- View 5: End-to-End Specimen & Laboratory Chain of Custody
-- Connects specimens from collection to lab request and result.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_lab_chain_of_custody AS
SELECT
    sp.specimen_id,
    sp.production_number,
    sp.specimen_type,
    sp.seal_no,
    sp.collection_date,
    sp.chain_of_custody_status,
    ce.event_id,
    ce.event_type,
    cm.case_number,
    lr.lab_request_id,
    lr.lab_name,
    lr.test_requested,
    lr.urgency,
    lr.date_sent,
    lr.receiving_refno,
    res.lab_result_id,
    res.laboratory_no,
    res.result_date,
    res.findings,
    CASE WHEN res.lab_result_id IS NOT NULL THEN 'Completed' ELSE 'Pending' END AS result_status
FROM specimen sp
JOIN case_event ce ON ce.event_id = sp.event_id
JOIN case_master cm ON cm.case_id = ce.case_id
LEFT JOIN lab_request lr ON lr.specimen_id = sp.specimen_id
LEFT JOIN lab_result res ON res.lab_request_id = lr.lab_request_id;

-- ------------------------------------------------------------
-- View 6: Staff Workload Statistics
-- Summarizes active cases assigned to each medical officer.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_staff_workload AS
SELECT
    s.staff_id,
    s.full_name,
    s.designation,
    s.station,
    COUNT(ca.case_id) AS total_assigned_cases,
    SUM(CASE WHEN cm.status <> 'Despatched' THEN 1 ELSE 0 END) AS active_cases,
    SUM(CASE WHEN cm.status = 'Despatched' THEN 1 ELSE 0 END) AS completed_cases
FROM staff s
LEFT JOIN case_assignment ca ON ca.staff_id = s.staff_id
LEFT JOIN case_master cm     ON cm.case_id = ca.case_id
GROUP BY s.staff_id, s.full_name, s.designation, s.station;
