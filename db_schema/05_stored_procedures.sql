-- ============================================================
-- FORENSIC MEDICO-LEGAL DATABASE
-- 05_stored_procedures.sql — Stored Procedures & Business Logic
-- ============================================================

-- ------------------------------------------------------------
-- Procedure 1: Atomic Case Registration
-- Registers a complete new case with patient, investigating officer, court, and primary staff assignment.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_register_case(
    p_case_number         VARCHAR(30),
    p_inquest_no          VARCHAR(30),
    p_case_type           VARCHAR(40),
    p_police_refno        VARCHAR(50),
    p_court_refno         VARCHAR(50),
    p_dept_refno          VARCHAR(50),
    p_incident_date       TIMESTAMP,
    p_patient_id          INT,
    p_police_station_id   INT,
    p_issuing_officer_id  INT,
    p_court_id            INT,
    p_magistrate_id       INT,
    p_assigned_staff_id   INT,
    p_staff_role          VARCHAR(50)
)
RETURNS INT AS $$
DECLARE
    v_new_case_id INT;
BEGIN
    -- Insert Master Case Record
    INSERT INTO case_master (
        case_number, inquest_no, case_type, police_refno, court_refno, dept_refno,
        incident_date, status, patient_id, police_station_id, issuing_officer_id,
        court_id, magistrate_id
    ) VALUES (
        p_case_number, p_inquest_no, p_case_type, p_police_refno, p_court_refno, p_dept_refno,
        p_incident_date, 'Under Examination', p_patient_id, p_police_station_id, p_issuing_officer_id,
        p_court_id, p_magistrate_id
    )
    RETURNING case_id INTO v_new_case_id;

    -- Assign Primary Medical Officer
    IF p_assigned_staff_id IS NOT NULL THEN
        INSERT INTO case_assignment (case_id, staff_id, role_in_case)
        VALUES (v_new_case_id, p_assigned_staff_id, COALESCE(p_staff_role, 'Examining JMO'));
    END IF;

    RETURN v_new_case_id;
END;
$$ LANGUAGE plpgsql;


-- ------------------------------------------------------------
-- Procedure 2: Submit Lab Request with Specimen
-- Records specimen collection and creates corresponding laboratory request.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_submit_lab_request(
    p_event_id             INT,
    p_specimen_type        VARCHAR(100),
    p_specimen_label       VARCHAR(10),
    p_seal_no              VARCHAR(30),
    p_production_number    VARCHAR(30),
    p_lab_name             VARCHAR(40),
    p_requested_by_staff_id INT,
    p_test_requested       TEXT,
    p_urgency              VARCHAR(15)
)
RETURNS INT AS $$
DECLARE
    v_specimen_id    INT;
    v_lab_request_id INT;
    v_case_id        INT;
BEGIN
    -- 1. Create Specimen Record
    INSERT INTO specimen (
        event_id, specimen_type, specimen_label, collection_date, seal_no,
        chain_of_custody_status, production_number
    ) VALUES (
        p_event_id, p_specimen_type, p_specimen_label, CURRENT_TIMESTAMP, p_seal_no,
        'Sent to ' || p_lab_name, p_production_number
    )
    RETURNING specimen_id INTO v_specimen_id;

    -- 2. Create Lab Request
    INSERT INTO lab_request (
        specimen_id, lab_name, requested_by_staff_id, test_requested, date_sent, urgency, request_purpose
    ) VALUES (
        v_specimen_id, p_lab_name, p_requested_by_staff_id, p_test_requested, CURRENT_TIMESTAMP, COALESCE(p_urgency, 'Routine'), 'Judicial'
    )
    RETURNING lab_request_id INTO v_lab_request_id;

    -- 3. Update Case Status to 'Awaiting Lab'
    SELECT case_id INTO v_case_id FROM case_event WHERE event_id = p_event_id;
    IF v_case_id IS NOT NULL THEN
        UPDATE case_master SET status = 'Awaiting Lab' WHERE case_id = v_case_id;
    END IF;

    RETURN v_lab_request_id;
END;
$$ LANGUAGE plpgsql;


-- ------------------------------------------------------------
-- Procedure 3: Despatch Report
-- Finalizes report issuance and marks case as 'Despatched'.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_despatch_report(
    p_report_id INT,
    p_file_path VARCHAR(255)
)
RETURNS BOOLEAN AS $$
DECLARE
    v_case_id INT;
BEGIN
    -- Update Report Record
    UPDATE report
    SET status = 'Despatched',
        date_despatched = CURRENT_TIMESTAMP,
        file_path = COALESCE(p_file_path, file_path)
    WHERE report_id = p_report_id
    RETURNING case_id INTO v_case_id;

    -- Update Master Case Status
    IF v_case_id IS NOT NULL THEN
        UPDATE case_master
        SET status = 'Despatched'
        WHERE case_id = v_case_id;
        RETURN TRUE;
    END IF;

    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;
