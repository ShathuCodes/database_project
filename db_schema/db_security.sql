-- ============================================================
-- DATABASE-LEVEL SECURITY, TRIGGERS & STORED PROCEDURES
-- ============================================================

-- 1. Create a native Database Audit Table 
-- This is completely independent of the application logic.
CREATE TABLE IF NOT EXISTS db_security_audit (
    audit_id        SERIAL PRIMARY KEY,
    table_name      VARCHAR(50),
    operation       VARCHAR(10),
    old_record_data JSONB,
    new_record_data JSONB,
    db_user         VARCHAR(50),
    changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Stored Procedure (Trigger Function)
-- This PL/pgSQL function will be called automatically by triggers.
CREATE OR REPLACE FUNCTION fn_audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO db_security_audit (table_name, operation, old_record_data, db_user)
        VALUES (TG_TABLE_NAME, 'DELETE', row_to_json(OLD)::JSONB, current_user);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO db_security_audit (table_name, operation, old_record_data, new_record_data, db_user)
        VALUES (TG_TABLE_NAME, 'UPDATE', row_to_json(OLD)::JSONB, row_to_json(NEW)::JSONB, current_user);
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO db_security_audit (table_name, operation, new_record_data, db_user)
        VALUES (TG_TABLE_NAME, 'INSERT', row_to_json(NEW)::JSONB, current_user);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 3. Attach Triggers to critical tables
DROP TRIGGER IF EXISTS trg_audit_case_master ON case_master;
CREATE TRIGGER trg_audit_case_master
AFTER INSERT OR UPDATE OR DELETE ON case_master
FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

DROP TRIGGER IF EXISTS trg_audit_postmortem ON postmortem;
CREATE TRIGGER trg_audit_postmortem
AFTER INSERT OR UPDATE OR DELETE ON postmortem
FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

DROP TRIGGER IF EXISTS trg_audit_report ON report;
CREATE TRIGGER trg_audit_report
AFTER INSERT OR UPDATE OR DELETE ON report
FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();


-- ============================================================
-- DATABASE ROLES (GRANT & REVOKE)
-- These commands define native PostgreSQL user roles representing
-- the organizational structure.
-- ============================================================

-- Create group roles (Without login permissions, just for grouping privileges)
DO $$ 
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'role_admin') THEN
    CREATE ROLE role_admin;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'role_jmo') THEN
    CREATE ROLE role_jmo;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'role_clerk') THEN
    CREATE ROLE role_clerk;
  END IF;
END
$$;

-- Revoke everything first to ensure a clean slate
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM role_admin, role_jmo, role_clerk;

-- Administrator Privileges: Full access to system/admin tables, BUT explicit denial to clinical data
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO role_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO role_admin;
-- Explicitly revoke access to medical data to enforce Separation of Duties (Medical Privacy)
REVOKE ALL PRIVILEGES ON patient, case_master, case_event, clinical_examination, postmortem, skeletal_examination, injury, sexual_assault_finding, postmortem_organ_finding, body_identifier, skeletal_item, specimen, lab_request, lab_request_organ_tissue, lab_result, report FROM role_admin;

-- JMO Privileges: Can manage cases and medical events, but cannot manage users/staff
GRANT SELECT, INSERT, UPDATE ON case_master, case_event, clinical_examination, postmortem, skeletal_examination, specimen, lab_request TO role_jmo;
GRANT SELECT ON patient, police_station, investigating_officer, court, magistrate TO role_jmo;
REVOKE DELETE ON case_master FROM role_jmo; -- Example of explicit deny
-- Cannot access security logs or users
REVOKE ALL ON app_user, staff, audit_log, db_security_audit FROM role_jmo;

-- Clerk Privileges: View-only access to most things, limited insert (e.g. registering a patient)
GRANT SELECT ON patient, case_master, report TO role_clerk;
GRANT INSERT, UPDATE ON patient TO role_clerk;
-- Explicitly block from medical data
REVOKE ALL PRIVILEGES ON postmortem, clinical_examination, skeletal_examination, sexual_assault_finding FROM role_clerk;
