-- ============================================================
--  FORENSIC MEDICAL DEPARTMENT DATABASE
--  PostgreSQL Schema
-- ============================================================

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS court_report CASCADE;
DROP TABLE IF EXISTS lab_test CASCADE;
DROP TABLE IF EXISTS evidence CASCADE;
DROP TABLE IF EXISTS postmortem CASCADE;
DROP TABLE IF EXISTS case_doctor CASCADE;
DROP TABLE IF EXISTS forensic_case CASCADE;
DROP TABLE IF EXISTS patient CASCADE;
DROP TABLE IF EXISTS app_user CASCADE;
DROP TABLE IF EXISTS staff CASCADE;

-- ============================================================
-- STAFF
-- ============================================================
CREATE TABLE staff (
    staff_id   SERIAL PRIMARY KEY,
    full_name  VARCHAR(100) NOT NULL,
    role       VARCHAR(30)  NOT NULL CHECK (role IN ('Hospital Management', 'Police Management')),
    specialization VARCHAR(100),
    contact    VARCHAR(20),
    email      VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- USERS (login accounts)
-- ============================================================
CREATE TABLE app_user (
    user_id    SERIAL PRIMARY KEY,
    username   VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role       VARCHAR(30) NOT NULL CHECK (role IN ('Hospital Management', 'Police Management')),
    staff_id   INT REFERENCES staff(staff_id) ON DELETE SET NULL,
    is_active  BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PATIENT
-- ============================================================
CREATE TABLE patient (
    patient_id  SERIAL PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    nic         VARCHAR(20)  UNIQUE,
    dob         DATE,
    gender      VARCHAR(10)  CHECK (gender IN ('Male','Female','Other')),
    address     TEXT,
    contact     VARCHAR(20),
    hospital_no VARCHAR(30),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- FORENSIC CASE
-- ============================================================
CREATE TABLE forensic_case (
    case_id        SERIAL PRIMARY KEY,
    patient_id     INT REFERENCES patient(patient_id) ON DELETE RESTRICT,
    case_number    VARCHAR(30) UNIQUE NOT NULL,
    case_type      VARCHAR(30) NOT NULL CHECK (case_type IN (
                       'Postmortem','Assault','Accident',
                       'Sexual Assault','Toxicology','Clinical')),
    incident_date  DATE,
    admission_date DATE DEFAULT CURRENT_DATE,
    police_ref     VARCHAR(50),
    court_ref      VARCHAR(50),
    police_station VARCHAR(100),
    magistrate     VARCHAR(100),
    status         VARCHAR(20) DEFAULT 'Open' CHECK (status IN ('Open','In Progress','Closed')),
    description    TEXT,
    created_by     INT REFERENCES app_user(user_id),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- CASE ↔ DOCTOR  (many-to-many)
-- ============================================================
CREATE TABLE case_doctor (
    case_id  INT REFERENCES forensic_case(case_id) ON DELETE CASCADE,
    staff_id INT REFERENCES staff(staff_id) ON DELETE CASCADE,
    assigned_date DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (case_id, staff_id)
);

-- ============================================================
-- POSTMORTEM
-- ============================================================
CREATE TABLE postmortem (
    pm_id         SERIAL PRIMARY KEY,
    case_id       INT REFERENCES forensic_case(case_id) ON DELETE CASCADE,
    doctor_id     INT REFERENCES staff(staff_id),
    exam_date     DATE,
    findings      TEXT,
    cause_of_death TEXT,
    manner_of_death VARCHAR(30) CHECK (manner_of_death IN (
                       'Natural','Homicide','Suicide','Accident','Undetermined')),
    body_condition VARCHAR(50),
    notes         TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- EVIDENCE
-- ============================================================
CREATE TABLE evidence (
    evidence_id      SERIAL PRIMARY KEY,
    case_id          INT REFERENCES forensic_case(case_id) ON DELETE CASCADE,
    evidence_type    VARCHAR(50) NOT NULL,
    description      TEXT,
    storage_location VARCHAR(100),
    collected_by     VARCHAR(100),
    collected_date   DATE,
    chain_of_custody TEXT,
    status           VARCHAR(20) DEFAULT 'In Storage' CHECK (status IN (
                         'In Storage','Sent to Lab','Returned','Disposed')),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- LABORATORY TEST
-- ============================================================
CREATE TABLE lab_test (
    test_id     SERIAL PRIMARY KEY,
    case_id     INT REFERENCES forensic_case(case_id) ON DELETE CASCADE,
    evidence_id INT REFERENCES evidence(evidence_id) ON DELETE SET NULL,
    test_type   VARCHAR(100) NOT NULL,
    requested_by INT REFERENCES staff(staff_id),
    tested_by   VARCHAR(100),
    test_date   DATE,
    result      TEXT,
    status      VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending','Completed','Failed')),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- COURT REPORT
-- ============================================================
CREATE TABLE court_report (
    report_id       SERIAL PRIMARY KEY,
    case_id         INT REFERENCES forensic_case(case_id) ON DELETE CASCADE,
    doctor_id       INT REFERENCES staff(staff_id),
    report_type     VARCHAR(50),
    content         TEXT,
    submission_date DATE,
    court_name      VARCHAR(100),
    status          VARCHAR(20) DEFAULT 'Draft' CHECK (status IN ('Draft','Submitted','Accepted','Rejected')),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- AUDIT LOG
-- ============================================================
CREATE TABLE audit_log (
    log_id     SERIAL PRIMARY KEY,
    user_id    INT REFERENCES app_user(user_id),
    action     VARCHAR(20) CHECK (action IN ('INSERT','UPDATE','DELETE','LOGIN','LOGOUT')),
    table_name VARCHAR(50),
    record_id  INT,
    details    TEXT,
    ip_address VARCHAR(45),
    timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_case_patient   ON forensic_case(patient_id);
CREATE INDEX idx_case_status    ON forensic_case(status);
CREATE INDEX idx_case_type      ON forensic_case(case_type);
CREATE INDEX idx_evidence_case  ON evidence(case_id);
CREATE INDEX idx_labtest_case   ON lab_test(case_id);
CREATE INDEX idx_report_case    ON court_report(case_id);
CREATE INDEX idx_audit_user     ON audit_log(user_id);
CREATE INDEX idx_audit_time     ON audit_log(timestamp);

-- ============================================================
-- USEFUL VIEWS
-- ============================================================

-- Full case summary joining patient
CREATE OR REPLACE VIEW v_case_summary AS
SELECT
    fc.case_id,
    fc.case_number,
    fc.case_type,
    fc.status,
    fc.incident_date,
    fc.admission_date,
    fc.police_ref,
    fc.court_ref,
    fc.police_station,
    p.full_name  AS patient_name,
    p.gender     AS patient_gender,
    p.nic        AS patient_nic
FROM forensic_case fc
LEFT JOIN patient p ON p.patient_id = fc.patient_id;

-- Open cases count per type
CREATE OR REPLACE VIEW v_stats_by_type AS
SELECT case_type, status, COUNT(*) AS total
FROM forensic_case
GROUP BY case_type, status;