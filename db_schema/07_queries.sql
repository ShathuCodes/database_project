-- ============================================================
-- FORENSIC MEDICO-LEGAL DATABASE
-- 07_queries.sql — Essential Operational & Statistical Queries
-- ============================================================

-- ------------------------------------------------------------
-- Query 1: Full Case Search by Patient NIC or Passport Number
-- Searches patient history across all past medico-legal examinations.
-- ------------------------------------------------------------
SELECT
    cm.case_number,
    cm.case_type,
    cm.status,
    cm.received_date,
    p.full_name AS patient_name,
    p.nic_passportno,
    ps.station_name AS police_station,
    c.court_name
FROM case_master cm
JOIN patient p ON p.patient_id = cm.patient_id
JOIN police_station ps ON ps.police_station_id = cm.police_station_id
JOIN court c ON c.court_id = cm.court_id
WHERE p.nic_passportno = '198512345678';


-- ------------------------------------------------------------
-- Query 2: Overdue Pending Lab Requests Tracking
-- Identifies specimens sent to external labs without received results over 7 days.
-- ------------------------------------------------------------
SELECT
    lr.lab_request_id,
    cm.case_number,
    cm.case_type,
    sp.specimen_type,
    sp.seal_no,
    lr.lab_name,
    lr.test_requested,
    lr.date_sent,
    CURRENT_DATE - lr.date_sent::date AS days_pending,
    s.full_name AS requested_by_doctor
FROM lab_request lr
JOIN specimen sp ON sp.specimen_id = lr.specimen_id
JOIN case_event ce ON ce.event_id = sp.event_id
JOIN case_master cm ON cm.case_id = ce.case_id
JOIN staff s ON s.staff_id = lr.requested_by_staff_id
LEFT JOIN lab_result res ON res.lab_request_id = lr.lab_request_id
WHERE res.lab_result_id IS NULL
ORDER BY days_pending DESC;


-- ------------------------------------------------------------
-- Query 3: Complete Medico-Legal Examination Details for a Case
-- Fetches Clinical Examination, Sexual Assault findings, or Postmortem findings.
-- ------------------------------------------------------------
SELECT
    cm.case_number,
    ce.event_type,
    ce.event_date,
    s.full_name AS jmo_name,
    pm.date_time_of_death,
    pm.place_of_examination,
    pm.cause_of_death,
    pm.conclusion
FROM case_master cm
JOIN case_event ce ON ce.case_id = cm.case_id
JOIN staff s ON s.staff_id = ce.staff_id
LEFT JOIN postmortem pm ON pm.event_id = ce.event_id
WHERE cm.case_number = 'MLC/2026/0143';


-- ------------------------------------------------------------
-- Query 4: Injury & Grievous Hurt Analysis
-- Retrieves all recorded injuries per case along with Penal Code clause descriptions.
-- ------------------------------------------------------------
SELECT
    cm.case_number,
    inj.nature,
    inj.site,
    inj.causative_weapon,
    inj.category_of_hurt,
    inj.endangers_life,
    gh.clause_code AS grievous_clause,
    gh.description AS grievous_clause_description,
    inj.explanatory_remarks
FROM injury inj
JOIN case_event ce ON ce.event_id = inj.event_id
JOIN case_master cm ON cm.case_id = ce.case_id
LEFT JOIN grievous_hurt_type gh ON gh.clause_code = inj.grievous_hurt_clause_code
WHERE cm.case_id = 1;


-- ------------------------------------------------------------
-- Query 5: Monthly Medico-Legal Case Distribution (Statistical Report)
-- Generates aggregate monthly breakdown of cases by type for departmental reporting.
-- ------------------------------------------------------------
SELECT
    TO_CHAR(received_date, 'YYYY-MM') AS month_year,
    case_type,
    COUNT(*) AS total_cases,
    SUM(CASE WHEN status = 'Despatched' THEN 1 ELSE 0 END) AS completed_reports,
    SUM(CASE WHEN status <> 'Despatched' THEN 1 ELSE 0 END) AS pending_reports
FROM case_master
GROUP BY TO_CHAR(received_date, 'YYYY-MM'), case_type
ORDER BY month_year DESC, case_type;


-- ------------------------------------------------------------
-- Query 6: Chain of Custody & Evidence Audit Log for Court Production
-- Fetches full chronological movement history for specimens in a court case.
-- ------------------------------------------------------------
SELECT
    cm.case_number,
    sp.production_number,
    sp.specimen_type,
    sp.seal_no,
    sp.collection_date,
    sp.chain_of_custody_status,
    lr.lab_name,
    lr.receiving_refno,
    res.laboratory_no,
    res.result_date,
    res.findings
FROM specimen sp
JOIN case_event ce ON ce.event_id = sp.event_id
JOIN case_master cm ON cm.case_id = ce.case_id
LEFT JOIN lab_request lr ON lr.specimen_id = sp.specimen_id
LEFT JOIN lab_result res ON res.lab_request_id = lr.lab_request_id
WHERE cm.case_number = 'MLC/2026/0143';
