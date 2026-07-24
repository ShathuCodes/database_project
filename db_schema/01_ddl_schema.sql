-- ============================================================
-- FORENSIC MEDICO-LEGAL DATABASE
-- 01_ddl_schema.sql — Core Data Definition Language (DDL)
-- PostgreSQL Schema
-- ============================================================

-- Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS report CASCADE;
DROP TABLE IF EXISTS lab_result CASCADE;
DROP TABLE IF EXISTS lab_request_organ_tissue CASCADE;
DROP TABLE IF EXISTS lab_request CASCADE;
DROP TABLE IF EXISTS specimen CASCADE;
DROP TABLE IF EXISTS skeletal_item CASCADE;
DROP TABLE IF EXISTS body_identifier CASCADE;
DROP TABLE IF EXISTS postmortem_organ_finding CASCADE;
DROP TABLE IF EXISTS sexual_assault_finding CASCADE;
DROP TABLE IF EXISTS injury CASCADE;
DROP TABLE IF EXISTS grievous_hurt_type CASCADE;
DROP TABLE IF EXISTS skeletal_examination CASCADE;
DROP TABLE IF EXISTS postmortem CASCADE;
DROP TABLE IF EXISTS clinical_examination CASCADE;
DROP TABLE IF EXISTS case_event CASCADE;
DROP TABLE IF EXISTS inquest_verdict CASCADE;
DROP TABLE IF EXISTS case_assignment CASCADE;
DROP TABLE IF EXISTS case_master CASCADE;
DROP TABLE IF EXISTS magistrate CASCADE;
DROP TABLE IF EXISTS court CASCADE;
DROP TABLE IF EXISTS investigating_officer CASCADE;
DROP TABLE IF EXISTS police_station CASCADE;
DROP TABLE IF EXISTS patient CASCADE;
DROP TABLE IF EXISTS notification CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS db_security_audit CASCADE;
DROP TABLE IF EXISTS app_user CASCADE;
DROP TABLE IF EXISTS staff CASCADE;
DROP TABLE IF EXISTS role CASCADE;

-- ============================================================
-- SECTION 1: SECURITY & ADMINISTRATION
-- ============================================================

CREATE TABLE role (
    role_id     SERIAL PRIMARY KEY,
    role_name   VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE staff (
    staff_id      SERIAL PRIMARY KEY,
    full_name     VARCHAR(100) NOT NULL,
    designation   VARCHAR(30) NOT NULL CHECK (designation IN
                   ('Senior JMO','JMO','PG Trainee','Tech Officer','Clerk')),
    slmc_regno    VARCHAR(30),
    qualification VARCHAR(150),
    station       VARCHAR(100),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE app_user (
    user_id        SERIAL PRIMARY KEY,
    username       VARCHAR(50) UNIQUE NOT NULL,
    password_hash  TEXT NOT NULL,
    role_id        INT NOT NULL REFERENCES role(role_id),
    staff_id       INT UNIQUE REFERENCES staff(staff_id) ON DELETE SET NULL,
    last_login     TIMESTAMP,
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_log (
    audit_log_id  SERIAL PRIMARY KEY,
    user_id       INT REFERENCES app_user(user_id),
    table_name    VARCHAR(50) NOT NULL,
    record_id     INT,
    action_type   VARCHAR(10) NOT NULL CHECK (action_type IN ('INSERT','UPDATE','DELETE')),
    old_values    TEXT,
    new_values    TEXT,
    ip_address    VARCHAR(45),
    "timestamp"   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE db_security_audit (
    audit_id        SERIAL PRIMARY KEY,
    table_name      VARCHAR(50) NOT NULL,
    operation       VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT','UPDATE','DELETE')),
    old_record_data JSONB,
    new_record_data JSONB,
    db_user         VARCHAR(50) DEFAULT CURRENT_USER,
    changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notification (
    notification_id SERIAL PRIMARY KEY,
    user_id          INT NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    title            VARCHAR(150) NOT NULL,
    message_text     TEXT,
    is_read          BOOLEAN DEFAULT FALSE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SECTION 2: PEOPLE & ORGANISATIONS
-- ============================================================

CREATE TABLE patient (
    patient_id       SERIAL PRIMARY KEY,
    full_name        VARCHAR(100) NOT NULL,
    nic_passportno   VARCHAR(30) UNIQUE,
    dob              DATE,
    age              INT,
    gender           VARCHAR(10) CHECK (gender IN ('M','F','Unknown')),
    address          TEXT,
    occupation       VARCHAR(100)
);

CREATE TABLE police_station (
    police_station_id SERIAL PRIMARY KEY,
    station_name       VARCHAR(100) NOT NULL,
    division           VARCHAR(100)
);

CREATE TABLE investigating_officer (
    officer_id         SERIAL PRIMARY KEY,
    name               VARCHAR(100) NOT NULL,
    rank               VARCHAR(50),
    officer_regno      VARCHAR(50),
    police_station_id  INT NOT NULL REFERENCES police_station(police_station_id)
);

CREATE TABLE court (
    court_id   SERIAL PRIMARY KEY,
    court_name VARCHAR(100) NOT NULL,
    district   VARCHAR(100)
);

CREATE TABLE magistrate (
    magistrate_id SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    court_id      INT NOT NULL REFERENCES court(court_id)
);

-- ============================================================
-- SECTION 3: CASE MASTER LOG
-- ============================================================

CREATE TABLE case_master (
    case_id             SERIAL PRIMARY KEY,
    case_number         VARCHAR(30) UNIQUE NOT NULL,
    inquest_no          VARCHAR(30),
    case_type           VARCHAR(40) NOT NULL CHECK (case_type IN
                         ('Assault','Sexual Assault','Homicide',
                          'Natural/Accidental Death','Skeletal Remains')),
    police_refno        VARCHAR(50),
    court_refno         VARCHAR(50),
    dept_refno          VARCHAR(50),
    incident_date       TIMESTAMP,
    received_date       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trial_date          TIMESTAMP,
    status              VARCHAR(20) DEFAULT 'Under Examination' CHECK (status IN
                         ('Under Examination','Awaiting Lab','Report Pending','Despatched')),
    patient_id          INT REFERENCES patient(patient_id),
    police_station_id   INT NOT NULL REFERENCES police_station(police_station_id),
    issuing_officer_id  INT REFERENCES investigating_officer(officer_id),
    producing_officer_id INT REFERENCES investigating_officer(officer_id),
    court_id            INT NOT NULL REFERENCES court(court_id),
    magistrate_id       INT REFERENCES magistrate(magistrate_id),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE case_assignment (
    case_id      INT NOT NULL REFERENCES case_master(case_id) ON DELETE CASCADE,
    staff_id     INT NOT NULL REFERENCES staff(staff_id) ON DELETE CASCADE,
    role_in_case VARCHAR(50),
    PRIMARY KEY (case_id, staff_id)
);

CREATE TABLE inquest_verdict (
    verdict_id    SERIAL PRIMARY KEY,
    case_id       INT UNIQUE NOT NULL REFERENCES case_master(case_id) ON DELETE CASCADE,
    magistrate_id INT NOT NULL REFERENCES magistrate(magistrate_id),
    verdict_text  TEXT,
    verdict_date  DATE
);

-- ============================================================
-- SECTION 4: CASE EVENTS & MEDICAL SUBTYPES
-- ============================================================

CREATE TABLE case_event (
    event_id    SERIAL PRIMARY KEY,
    case_id     INT NOT NULL REFERENCES case_master(case_id) ON DELETE CASCADE,
    event_type  VARCHAR(30) NOT NULL CHECK (event_type IN
                ('Clinical Examination','Postmortem','Skeletal Examination')),
    event_date  TIMESTAMP NOT NULL,
    staff_id    INT NOT NULL REFERENCES staff(staff_id)
);

CREATE TABLE clinical_examination (
    event_id                 INT PRIMARY KEY REFERENCES case_event(event_id) ON DELETE CASCADE,
    history_given            TEXT,
    place_of_exam             VARCHAR(100),
    hospital_no               VARCHAR(30),
    ward                      VARCHAR(30),
    bed_no                    VARCHAR(20),
    admission_date            DATE,
    discharge_date            DATE,
    consent_obtained          BOOLEAN,
    reason_for_referral       TEXT,
    alcohol_smell_present     BOOLEAN,
    under_influence_alcohol   VARCHAR(10) CHECK (under_influence_alcohol IN ('Yes','No','Uncertain')),
    drugs_consumed            VARCHAR(15) CHECK (drugs_consumed IN ('Yes','No','Not tested')),
    under_influence_drugs     VARCHAR(15) CHECK (under_influence_drugs IN ('Yes','No','Not tested')),
    investigations_ordered    TEXT,
    referrals_made            TEXT,
    other_opinions            TEXT
);

CREATE TABLE postmortem (
    event_id                INT PRIMARY KEY REFERENCES case_event(event_id) ON DELETE CASCADE,
    date_time_of_death      TIMESTAMP,
    requested_by_name       VARCHAR(100),
    requested_by_designation VARCHAR(100),
    district                VARCHAR(100),
    place_of_examination    VARCHAR(150),
    scene_description       TEXT,
    external_exam_description TEXT,
    estimated_age           VARCHAR(30),
    sex                     VARCHAR(10) CHECK (sex IN ('M','F','Unknown')),
    height_cm               DECIMAL(5,2),
    eyes_and_pupils         VARCHAR(150),
    hair_description        VARCHAR(150),
    teeth_condition         VARCHAR(150),
    tongue_condition        VARCHAR(150),
    primary_flaccidity      VARCHAR(100),
    rigor_mortis            VARCHAR(100),
    hypostasis              VARCHAR(100),
    putrefaction            VARCHAR(100),
    hands_nails_condition   VARCHAR(150),
    cause_of_death          TEXT,
    time_since_death        VARCHAR(100),
    register_serial_no      VARCHAR(30),
    conclusion              TEXT,
    UNIQUE (district, register_serial_no)
);

CREATE TABLE skeletal_examination (
    event_id                     INT PRIMARY KEY REFERENCES case_event(event_id) ON DELETE CASCADE,
    history                      TEXT,
    specimen_no                  VARCHAR(30) UNIQUE,
    place_found                  TEXT,
    seal_status                  VARCHAR(15) CHECK (seal_status IN ('Intact','Broken','No Seal')),
    wrapping_description         TEXT,
    human_remains_present        BOOLEAN,
    animal_remains_present       BOOLEAN,
    state_of_putrefaction        VARCHAR(100),
    skeletonized                 BOOLEAN,
    mummified                    BOOLEAN,
    min_no_individuals           INT,
    mni_reasons                  TEXT,
    gender_conclusion            VARCHAR(150),
    age_conclusion               VARCHAR(150),
    stature_estimate              VARCHAR(50),
    stature_method                VARCHAR(100),
    time_since_death              VARCHAR(150),
    cause_of_death_opinion        TEXT,
    special_techniques_recommended TEXT,
    supervised_by_staff_id        INT REFERENCES staff(staff_id)
);

CREATE TABLE grievous_hurt_type (
    clause_code VARCHAR(5) PRIMARY KEY,
    description TEXT NOT NULL
);

CREATE TABLE injury (
    injury_id                INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id                 INT NOT NULL REFERENCES case_event(event_id) ON DELETE CASCADE,
    nature                   VARCHAR(100),
    size_shape               VARCHAR(100),
    site                     TEXT,
    causative_weapon         VARCHAR(100),
    body_cavity              VARCHAR(10) CHECK (body_cavity IN ('External','Internal')),
    category_of_hurt         VARCHAR(40) CHECK (category_of_hurt IN
                             ('Non-grievous','Grievous','Fatal in ordinary course of nature')),
    endangers_life           BOOLEAN DEFAULT FALSE,
    timing_relative_to_death VARCHAR(20) CHECK (timing_relative_to_death IN
                             ('Ante-mortem','Post-mortem','Not Applicable')),
    grievous_hurt_clause_code VARCHAR(5) REFERENCES grievous_hurt_type(clause_code),
    explanatory_remarks      TEXT
);

CREATE TABLE sexual_assault_finding (
    event_id                             INT PRIMARY KEY REFERENCES clinical_examination(event_id) ON DELETE CASCADE,
    history_of_assault_given             TEXT,
    vaginal_hymen_signs_present          BOOLEAN,
    anal_penetration_signs_present       BOOLEAN,
    inter_labial_penetration_signs_present BOOLEAN,
    remarks                              TEXT
);

CREATE TABLE postmortem_organ_finding (
    organ_finding_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id         INT NOT NULL REFERENCES postmortem(event_id) ON DELETE CASCADE,
    organ_name       VARCHAR(100) NOT NULL,
    findings         TEXT
);

CREATE TABLE body_identifier (
    identifier_id            INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id                 INT NOT NULL REFERENCES postmortem(event_id) ON DELETE CASCADE,
    name                     VARCHAR(100) NOT NULL,
    address                  TEXT,
    relationship_to_deceased VARCHAR(50)
);

CREATE TABLE skeletal_item (
    item_id       INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id      INT NOT NULL REFERENCES skeletal_examination(event_id) ON DELETE CASCADE,
    item_category VARCHAR(20) NOT NULL CHECK (item_category IN ('Human Remain','Other Content')),
    description   TEXT,
    serial_number VARCHAR(30),
    quantity      INT DEFAULT 1
);

-- ============================================================
-- SECTION 5: SPECIMENS & LABORATORY CHAIN
-- ============================================================

CREATE TABLE specimen (
    specimen_id           INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id              INT NOT NULL REFERENCES case_event(event_id) ON DELETE CASCADE,
    specimen_type         VARCHAR(100),
    specimen_label        VARCHAR(10),
    collection_date       TIMESTAMP,
    seal_no               VARCHAR(30),
    chain_of_custody_status VARCHAR(50),
    production_number     VARCHAR(30)
);

CREATE TABLE lab_request (
    lab_request_id       SERIAL PRIMARY KEY,
    specimen_id          INT NOT NULL REFERENCES specimen(specimen_id) ON DELETE CASCADE,
    lab_name             VARCHAR(40) NOT NULL CHECK (lab_name IN
                          ('Government Analyst','Histopathology','Microbiology','Medical Research Institute (MRI)')),
    requested_by_staff_id INT NOT NULL REFERENCES staff(staff_id),
    test_requested        TEXT,
    poisons_suspected      TEXT,
    macroscopic_appearances TEXT,
    special_procedure_request TEXT,
    date_sent              TIMESTAMP,
    urgency                 VARCHAR(15) CHECK (urgency IN ('Routine','Urgent','Storage')),
    request_purpose         VARCHAR(15) CHECK (request_purpose IN ('Judicial','Academic')),
    date_accepted            TIMESTAMP,
    accepted_by_name         VARCHAR(100),
    receiving_refno           VARCHAR(30)
);

CREATE TABLE lab_request_organ_tissue (
    lab_request_organ_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lab_request_id       INT NOT NULL REFERENCES lab_request(lab_request_id) ON DELETE CASCADE,
    organ_name            VARCHAR(100),
    no_of_tissue           INT
);

CREATE TABLE lab_result (
    lab_result_id  SERIAL PRIMARY KEY,
    lab_request_id INT UNIQUE NOT NULL REFERENCES lab_request(lab_request_id) ON DELETE CASCADE,
    laboratory_no  VARCHAR(30),
    result_date    TIMESTAMP,
    received_by    VARCHAR(100),
    lab_notes      TEXT,
    findings       TEXT,
    reported_by    VARCHAR(100),
    checked_by     VARCHAR(100),
    sent_on_date   TIMESTAMP
);

-- ============================================================
-- SECTION 6: REPORTS
-- ============================================================

CREATE TABLE report (
    report_id            SERIAL PRIMARY KEY,
    serial_no            VARCHAR(30),
    case_id              INT NOT NULL REFERENCES case_master(case_id) ON DELETE CASCADE,
    event_id             INT REFERENCES case_event(event_id),
    report_type          VARCHAR(20) NOT NULL CHECK (report_type IN ('MLR','PMR','Court Report')),
    prepared_by_staff_id INT NOT NULL REFERENCES staff(staff_id),
    date_issued          TIMESTAMP,
    date_despatched      TIMESTAMP,
    status               VARCHAR(15) DEFAULT 'Draft' CHECK (status IN ('Draft','Signed','Despatched')),
    file_path            VARCHAR(255)
);

-- ============================================================
-- SECTION 7: INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================

CREATE INDEX idx_case_patient        ON case_master(patient_id);
CREATE INDEX idx_case_status         ON case_master(status);
CREATE INDEX idx_case_type           ON case_master(case_type);
CREATE INDEX idx_event_case          ON case_event(case_id);
CREATE INDEX idx_specimen_event      ON specimen(event_id);
CREATE INDEX idx_labrequest_specimen ON lab_request(specimen_id);
CREATE INDEX idx_report_case         ON report(case_id);
CREATE INDEX idx_injury_event        ON injury(event_id);
CREATE INDEX idx_audit_user          ON audit_log(user_id);
CREATE INDEX idx_audit_time          ON audit_log("timestamp");
CREATE INDEX idx_notification_user   ON notification(user_id);