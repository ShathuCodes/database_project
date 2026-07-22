-- ============================================================
-- FORENSIC MEDICO-LEGAL DATABASE
-- 06_security_and_rbac.sql — Database Security & RBAC
-- PostgreSQL Security, Role-Based Access Control, & Auditing
-- ============================================================

-- ------------------------------------------------------------
-- 1. DATABASE SECURITY AUDIT TABLE
-- Independent system audit table tracking raw DB user mutations.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS db_security_audit (
    audit_id        SERIAL PRIMARY KEY,
    table_name      VARCHAR(50) NOT NULL,
    operation       VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT','UPDATE','DELETE')),
    old_record_data JSONB,
    new_record_data JSONB,
    db_user         VARCHAR(50) DEFAULT CURRENT_USER,
    changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 2. NATIVE DATABASE AUDIT TRIGGER FUNCTION
-- Captures row-level mutations into db_security_audit.
-- ------------------------------------------------------------
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

-- Attach Security Audit Triggers
DROP TRIGGER IF EXISTS trg_db_sec_audit_case_master ON case_master;
CREATE TRIGGER trg_db_sec_audit_case_master
AFTER INSERT OR UPDATE OR DELETE ON case_master
FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

DROP TRIGGER IF EXISTS trg_db_sec_audit_postmortem ON postmortem;
CREATE TRIGGER trg_db_sec_audit_postmortem
AFTER INSERT OR UPDATE OR DELETE ON postmortem
FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

DROP TRIGGER IF EXISTS trg_db_sec_audit_report ON report;
CREATE TRIGGER trg_db_sec_audit_report
AFTER INSERT OR UPDATE OR DELETE ON report
FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();


-- ------------------------------------------------------------
-- 3. ROLE-BASED ACCESS CONTROL (RBAC)
-- Defensively creates database roles and assigns privilege scopes.
-- ------------------------------------------------------------

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
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'role_tech_officer') THEN
    CREATE ROLE role_tech_officer;
  END IF;
END
$$;

-- Reset permissions to establish clean baseline
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM role_admin, role_jmo, role_clerk, role_tech_officer;

-- Administrator Privileges: Administrative & User management tables
GRANT SELECT, INSERT, UPDATE, DELETE ON role, staff, app_user, audit_log, notification TO role_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO role_admin;
REVOKE ALL PRIVILEGES ON patient, case_master, case_event, clinical_examination, postmortem, skeletal_examination, injury, sexual_assault_finding, postmortem_organ_finding, body_identifier, skeletal_item, specimen, lab_request, lab_request_organ_tissue, lab_result, report FROM role_admin;

-- JMO Privileges: Medical examination & case management
GRANT SELECT, INSERT, UPDATE ON case_master, case_event, clinical_examination, postmortem, skeletal_examination, sexual_assault_finding, postmortem_organ_finding, body_identifier, skeletal_item, injury, specimen, lab_request, report TO role_jmo;
GRANT SELECT ON patient, police_station, investigating_officer, court, magistrate, grievous_hurt_type TO role_jmo;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO role_jmo;
REVOKE DELETE ON case_master FROM role_jmo;
REVOKE ALL ON app_user, staff, audit_log, db_security_audit FROM role_jmo;

-- Lab Tech Privileges: Specimen tracking & lab results
GRANT SELECT, INSERT, UPDATE ON specimen, lab_request, lab_request_organ_tissue, lab_result TO role_tech_officer;
GRANT SELECT ON case_master, case_event TO role_tech_officer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO role_tech_officer;

-- Clerk Privileges: Patient & Case intake lookup
GRANT SELECT ON patient, police_station, investigating_officer, court, magistrate, case_master, report TO role_clerk;
GRANT INSERT, UPDATE ON patient, case_master TO role_clerk;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO role_clerk;
REVOKE ALL PRIVILEGES ON postmortem, clinical_examination, skeletal_examination, sexual_assault_finding FROM role_clerk;
