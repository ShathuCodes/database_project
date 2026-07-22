-- ============================================================
-- FORENSIC MEDICO-LEGAL DATABASE
-- 04_triggers_and_functions.sql — Triggers & Trigger Functions
-- ============================================================

-- ------------------------------------------------------------
-- 1. Automated Audit Logging Trigger Function
-- Records INSERT, UPDATE, DELETE operations on target tables into audit_log.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_audit_log_change()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id INT;
    v_record_id INT;
BEGIN
    -- Try to capture current user ID if set in session setting (e.g. SET LOCAL app.current_user_id = '1')
    BEGIN
        v_user_id := current_setting('app.current_user_id')::INT;
    EXCEPTION WHEN OTHERS THEN
        v_user_id := NULL;
    END;

    IF (TG_OP = 'DELETE') THEN
        v_record_id := OLD.case_id; -- Default fallback or primary key resolution
        INSERT INTO audit_log (user_id, table_name, record_id, action_type, old_values, new_values)
        VALUES (v_user_id, TG_TABLE_NAME, v_record_id, 'DELETE', row_to_json(OLD)::text, NULL);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        v_record_id := NEW.case_id;
        INSERT INTO audit_log (user_id, table_name, record_id, action_type, old_values, new_values)
        VALUES (v_user_id, TG_TABLE_NAME, v_record_id, 'UPDATE', row_to_json(OLD)::text, row_to_json(NEW)::text);
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        v_record_id := NEW.case_id;
        INSERT INTO audit_log (user_id, table_name, record_id, action_type, old_values, new_values)
        VALUES (v_user_id, TG_TABLE_NAME, v_record_id, 'INSERT', NULL, row_to_json(NEW)::text);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Attach Audit Log Trigger to Case Master
DROP TRIGGER IF EXISTS trg_audit_case_master ON case_master;
CREATE TRIGGER trg_audit_case_master
AFTER INSERT OR UPDATE OR DELETE ON case_master
FOR EACH ROW EXECUTE FUNCTION fn_audit_log_change();


-- ------------------------------------------------------------
-- 2. Automatic Case Status Transition Trigger Function
-- Automatically updates Case Status when a Lab Result is entered.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_update_case_status_on_lab_result()
RETURNS TRIGGER AS $$
DECLARE
    v_case_id INT;
BEGIN
    -- Find case_id linked to the lab request specimen
    SELECT ce.case_id INTO v_case_id
    FROM lab_request lr
    JOIN specimen sp ON sp.specimen_id = lr.specimen_id
    JOIN case_event ce ON ce.event_id = sp.event_id
    WHERE lr.lab_request_id = NEW.lab_request_id;

    IF v_case_id IS NOT NULL THEN
        -- Update case status to 'Report Pending' if currently 'Awaiting Lab'
        UPDATE case_master
        SET status = 'Report Pending'
        WHERE case_id = v_case_id AND status = 'Awaiting Lab';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_lab_result_case_status ON lab_result;
CREATE TRIGGER trg_lab_result_case_status
AFTER INSERT ON lab_result
FOR EACH ROW EXECUTE FUNCTION fn_update_case_status_on_lab_result();


-- ------------------------------------------------------------
-- 3. Automatic Notification Trigger Function
-- Generates a system notification when staff is assigned to a case.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_notify_on_case_assignment()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id INT;
    v_case_number VARCHAR(30);
    v_case_type VARCHAR(40);
BEGIN
    -- Resolve app_user ID linked to staff
    SELECT user_id INTO v_user_id FROM app_user WHERE staff_id = NEW.staff_id;

    -- Resolve case details
    SELECT case_number, case_type INTO v_case_number, v_case_type FROM case_master WHERE case_id = NEW.case_id;

    IF v_user_id IS NOT NULL THEN
        INSERT INTO notification (user_id, title, message_text)
        VALUES (
            v_user_id,
            'New Case Assignment',
            'You have been assigned as ' || COALESCE(NEW.role_in_case, 'Assigned Officer') || ' for case ' || v_case_number || ' (' || v_case_type || ').'
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_notify_case_assignment ON case_assignment;
CREATE TRIGGER trg_notify_case_assignment
AFTER INSERT ON case_assignment
FOR EACH ROW EXECUTE FUNCTION fn_notify_on_case_assignment();
